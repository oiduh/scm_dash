import numpy as np
from numpy.typing import NDArray
from typing import Any, TypeVar, Literal
import ast
import string
from dataclasses import dataclass, field


#
# supported 'builtin' functions
#


# trignometry
sin = np.sin
cos = np.cos
tan = np.tan
arcsin = np.arcsin
arccos = np.arccos
arctan = np.arctan
arctan2 = np.arctan2

# hyperbolic
sinh = np.sinh
cosh = np.cosh
tanh = np.tanh
arcsinh = np.arcsinh
arccosh = np.arccosh
arctanh = np.arctanh

# rounding
round = np.round
floor = np.floor
ceil = np.ceil

# exponents and logarithms
exp = np.exp
log = np.log
log10 = np.log10
log2 = np.log2

# misc
sqrt = np.sqrt
clip = np.clip
cbrt = np.cbrt
fabs = np.fabs


@dataclass
class Formula:
    text: str = ""
    verified: bool = False


@dataclass
class MechanismMetadata:
    mechanism_type: Literal["regression", "classification"] = "regression"
    # mapping from class_id to formula -> relevant for multi-class-classification
    formulas: dict[str, Formula] = field(
        default_factory=lambda: {str(id): Formula() for id in string.digits}
    )


@dataclass
class MechanismResult:
    success: bool
    values: NDArray | None


class BaseMechanism:
    def __init__(self, formulas: list[str], inputs: dict[str, list[float]]):
        self.formulas = formulas
        self.inputs = inputs
        self.values = {k: np.array(v, dtype=np.float128) for k, v in self.inputs.items()}

    def transform(self) -> MechanismResult:
        raise NotImplementedError()


class RegressionMechanism(BaseMechanism):
    def transform(self) -> MechanismResult:
        tree = ast.parse(self.formulas[0])
        for node in ast.walk(tree):
            # replace variables with inputs
            if isinstance(node, ast.Name) and node.id in self.inputs.keys():
                node.id = f"self.values[\"{node.id}\"]"
        new_formula = ast.unparse(tree)
        try:
            result: NDArray[np.float64] = eval(new_formula)
        except Exception as e:
            print(e)
            return MechanismResult(False, None)

        return MechanismResult(True, result)


class ClassificationMechanism(BaseMechanism):
    def transform(self) -> MechanismResult:
        # dimensions: x(number of classes), y(number of inputs) -> each input can have own dimension
        self.inputs = {k: np.array(v).flatten() for k, v in self.inputs.items()}
        results = np.full((len(self.formulas), len(list(self.inputs.values())[0])), False)

        failed = False
        for idx, formula in enumerate(self.formulas):
            tree = ast.parse(formula)
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id in self.inputs.keys():
                    node.id = f"self.values[\"{node.id}\"]"
            new_formula = ast.unparse(tree)
            try:
                result: NDArray[Any] = eval(new_formula)
                assert result.dtype == bool, "NOT A BOOL"
                results[idx] = result
            except Exception as e:
                failed = True
                print(e)
        if failed:
            return MechanismResult(False, None)

        if np.any(np.sum(results, axis=0) > 1.0):
            return MechanismResult(False, None)

        results = np.vstack([results, np.full(len(list(self.inputs.values())[0]), False)])
        for idx, col in enumerate(np.sum(results, axis=0)):
            if col == 0:
                results[-1][idx] = True

        if np.prod(np.sum(results, axis=0)) != 1.:
            return MechanismResult(False, None)

        return MechanismResult(True, results)
