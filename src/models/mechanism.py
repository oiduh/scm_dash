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


MechanismType = Literal["regression", "classification"]
MechanismState = Literal["editable", "locked"]


@dataclass
class MechanismMetadata:
    mechanism_type: MechanismType = "regression"
    state: MechanismState = "editable"
    valid: bool = True
    # mapping from class_id to formula -> only relevant for multi-class-classification
    formulas: dict[str, str | None] = field(init=False)

    def __post_init__(self) -> None:
        self.formulas = MechanismMetadata.reset_formulas()

    @staticmethod
    def reset_formulas() -> dict[str, str | None]:
        ret: dict[str, str | None] = {id_: None for id_ in string.digits}
        ret["0"] = "<PLACEHOLDER>"
        return ret

    def get_formulas(self):
        return {k: v for k, v in self.formulas.items() if v is not None}

    def get_class_by_id(self, id_: str) -> str | None:
        return self.formulas.get(id_)

    def get_free_class_ids(self) -> list[str]:
        return [id_ for id_, formula in self.formulas.items() if formula is None]

    def get_next_free_class_id(self) -> str | None:
        free_class_ids = self.get_free_class_ids()
        return free_class_ids[0] if len(free_class_ids) > 0 else None

    def add_class(self) -> None:
        assert self.mechanism_type == "classification"
        assert self.state == "editable"
        free_id = self.get_next_free_class_id()
        if free_id is None:
            raise Exception("Cannot add another class")
        self.formulas[free_id] = "<PLACEHOLDER>"

    def remove_class(self, class_id: str) -> None:
        assert self.state == "editable"
        if class_id not in self.formulas.keys() or self.formulas[class_id] is None:
            raise Exception("Cannot remove this class")
        self.formulas[class_id] = None


@dataclass
class MechanismResult:
    values: NDArray | None
    error: str | None


class BaseMechanism:
    def __init__(self, formulas: list[str], inputs: dict[str, np.ndarray]):
        self.formulas = formulas
        self.inputs = inputs
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
            return MechanismResult(None, "Failed to evaluate formula")

        return MechanismResult(result, None)


class ClassificationMechanism(BaseMechanism):
    def transform(self) -> MechanismResult:
        # dimensions: x(number of classes), y(number of inputs) -> each input can have own dimension
        self.inputs = {k: np.array(v).flatten() for k, v in self.inputs.items()}
        results = np.full(
            len(list(self.inputs.values())[0]), fill_value=-1, dtype=np.int32
        )

        failed_indices: list[int] = []
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
                            raise
                        else:
                            results[idx_] = idx
            except:
                failed_indices.append(idx)

        if len(failed_indices) > 0:
            return MechanismResult(
                None, f"Failed to evaluate classes: {failed_indices}"
            )

        else_class_idx = len(self.formulas)
        for idx_, x in enumerate(results):
            if x == -1:
                results[idx_] = else_class_idx

        return MechanismResult(results, None)
