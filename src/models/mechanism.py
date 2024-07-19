import ast
import string
from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray

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
    enabled: bool = False


MechanismType = Literal["regression", "classification"]


@dataclass
class MechanismMetadata:
    mechanism_type: MechanismType = "regression"
    # mapping from class_id to formula -> only relevant for multi-class-classification
    formulas: dict[str, Formula] = field(init=False)

    def __post_init__(self) -> None:
        self.formulas = MechanismMetadata.reset_formulas()

    @staticmethod
    def reset_formulas() -> dict[str, Formula]:
        ret = {str(id_): Formula() for id_ in string.digits}
        ret["0"].enabled = True
        return ret

    def change_type(self, new_type: Literal["regression", "classification"]) -> None:
        self.mechanism_type = new_type
        self.formulas = MechanismMetadata.reset_formulas()

    def get_class_by_id(self, id_: str) -> Formula | None:
        return self.formulas.get(id_)

    def get_free_class_ids(self) -> list[str]:
        return [
            id_ for id_, formula in self.formulas.items() if formula.enabled is False
        ]

    def get_next_free_class_id(self) -> str | None:
        free_class_ids = self.get_free_class_ids()
        return free_class_ids[0] if len(free_class_ids) > 0 else None

    def add_class(self) -> None:
        assert self.mechanism_type == "classification"
        free_id = self.get_next_free_class_id()
        if free_id is None:
            raise Exception("Cannot add another class")
        self.formulas[free_id].enabled = True

    def remove_class(self, class_id: str) -> None:
        if class_id not in self.formulas or self.formulas[class_id].enabled is False:
            raise Exception("Cannot remove this class")
        self.formulas[class_id].enabled = False

    def is_verified(self) -> bool:
        return all(x.verified for x in self.formulas.values() if x.enabled is True)


@dataclass
class MechanismResult:
    values: NDArray | None
    error: str | None


class BaseMechanism:
    def __init__(self, formulas: list[str], inputs: dict[str, np.ndarray]):
        self.formulas = formulas
        self.inputs = inputs
        # input consists of all data from in nodes, also own noise
        self.values = {k: np.array(v, dtype=np.float64) for k, v in self.inputs.items()}

    def transform(self) -> MechanismResult:
        raise NotImplementedError()


class RegressionMechanism(BaseMechanism):
    def transform(self) -> MechanismResult:
        tree = ast.parse(self.formulas[0])
        for node in ast.walk(tree):
            # replace variables with inputs
            if isinstance(node, ast.Name) and node.id in self.inputs.keys():
                node.id = f'self.values["{node.id}"]'
        new_formula = ast.unparse(tree)
        try:
            result: NDArray[np.float64] = eval(new_formula)
        except:
            return MechanismResult(None, "failed to evaluate")

        return MechanismResult(result, None)


class ClassificationMechanism(BaseMechanism):
    def transform(self) -> MechanismResult:
        # dimensions: x(number of classes), y(number of inputs) -> each input can have own dimension
        self.inputs = {k: np.array(v).flatten() for k, v in self.inputs.items()}
        results = np.full(
            len(list(self.inputs.values())[0]), fill_value=-1, dtype=np.int32
        )

        failed = False
        for idx, formula in enumerate(self.formulas):
            tree = ast.parse(formula)
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id in self.inputs.keys():
                    node.id = f'self.values["{node.id}"]'
            new_formula = ast.unparse(tree)
            try:
                result: np.ndarray[Any, np.dtype[np.bool_]] = eval(new_formula)
                assert result.dtype == np.bool_, "NOT A BOOL"
                for idx_, x in enumerate(result):
                    if bool(x) is True:
                        if results[idx_] != -1:
                            raise Exception("multi class")
                        else:
                            results[idx_] = idx
            except Exception as e:
                failed = True
                # TODO: logger
                print(e)

        if failed:
            return MechanismResult(None, "Failed to evaulate")

        else_class_idx = len(self.formulas)
        for idx_, x in enumerate(results):
            if x == -1:
                results[idx_] = else_class_idx

        return MechanismResult(results, None)
