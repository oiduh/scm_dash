import ast
import string
from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray
from utils.parser import Calc

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
cbrt = np.cbrt
abs = np.fabs


MechanismType = Literal["regression", "classification"]
MechanismState = Literal["editable", "locked"]


@dataclass
class MechanismMetadata:
    var_name: str
    mechanism_type: MechanismType = "regression"
    state: MechanismState = "editable"
    valid: bool = True
    formulas: dict[str, str | None] = field(init=False)  # depends on the type

    def __post_init__(self) -> None:
        self.reset_formulas()

    def reset_formulas(self) -> None:
        new_formulas: dict[str, str | None] = {id_: None for id_ in string.digits}
        if self.mechanism_type == "regression":
            new_formulas["0"] = "<invalid>"
        else:
            new_formulas["0"] = "<invalid>"
        self.formulas = new_formulas

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
        self.formulas[free_id] = "<invalid>"

    def remove_class(self, class_id: str) -> None:
        assert self.state == "editable"
        if class_id not in self.formulas.keys() or self.formulas[class_id] is None:
            raise Exception("Cannot remove this class")
        self.formulas[class_id] = None


@dataclass
class MechanismResult:
    values: NDArray | None
    error: Literal["class_overlap", "invalid_formula"] | None


class BaseMechanism:
    def __init__(self, formulas: list[str], inputs: dict[str, np.ndarray]):
        self.formulas = formulas
        self.inputs = inputs
        self.values = {k: np.array(v, dtype=np.float64) for k, v in self.inputs.items()}

    def transform(self) -> MechanismResult:
        raise NotImplementedError()


class RegressionMechanism(BaseMechanism):
    def transform(self) -> MechanismResult:
        calc = Calc()
        calc.run_example(self.formulas[0], self.inputs)
        if len(calc.errors) > 0:
            return MechanismResult(None, "invalid_formula")

        tree = ast.parse(self.formulas[0])
        for node in ast.walk(tree):
            # replace variables with inputs
            if isinstance(node, ast.Name) and node.id in self.inputs.keys():
                node.id = f'self.values["{node.id}"]'
        new_formula = ast.unparse(tree)
        try:
            result: NDArray[np.float64] = eval(new_formula)
        except:
            return MechanismResult(None, "invalid_formula")

        return MechanismResult(result, None)


class ClassificationMechanism(BaseMechanism):
    def transform(self) -> MechanismResult:
        # dimensions: x(number of classes), y(number of inputs) -> each input can have own dimension
        self.inputs = {k: np.array(v).flatten() for k, v in self.inputs.items()}

        calc = Calc()
        print()
        print(f"{self.inputs=}")
        for formula in self.formulas:
            print(f"{formula=}")
            calc.run_example(formula, self.inputs)
        print()
        if len(calc.errors) > 0:
            print(calc.errors)
            return MechanismResult(None, "invalid_formula")

        results = np.full(
            len(list(self.inputs.values())[0]), fill_value=-1, dtype=np.int32
        )

        for idx, formula in enumerate(self.formulas):
            tree = ast.parse(formula)
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id in self.inputs.keys():
                    node.id = f'self.values["{node.id}"]'
            new_formula = ast.unparse(tree)
            try:
                result: np.ndarray[Any, np.dtype[np.bool_]] = eval(new_formula)
                assert result.dtype == np.bool_, "NOT A BOOL"
            except Exception:
                return MechanismResult(None, "invalid_formula")

            for idx_, x in enumerate(result):
                if bool(x) is True:
                    if results[idx_] != -1:
                        return MechanismResult(None, "class_overlap")
                    else:
                        results[idx_] = idx

        # fill all unassigned results to 'other'
        else_class_idx = len(self.formulas)
        for idx_, x in enumerate(results):
            if x == -1:
                results[idx_] = else_class_idx

        return MechanismResult(results, None)
