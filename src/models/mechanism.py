import numpy as np
from numpy.typing import NDArray
from typing import Any
import ast


class BaseMechanism:
    def __init__(self, formulas: list[str], inputs: dict[str, list[float]]):
        self.formulas = formulas
        self.inputs = inputs

    def transform(self):
        raise NotImplementedError()


class RegressionMechanism(BaseMechanism):
    def transform(self):
        tree = ast.parse(self.formulas[0])
        for node in ast.walk(tree):
            # replace variables with inputs
            if isinstance(node, ast.Name) and node.id in self.inputs.keys():
                node.id = f"self.inputs[\"{node.id}\"]"
        new_formula = ast.unparse(tree)
        try:
            result: NDArray[np.float64] = eval(new_formula)
        except Exception as e:
            print(e)
            result = np.zeros(len(list(self.inputs.values())[0]))

        return result


class ClassificationMechanism(BaseMechanism):
    def transform(self):
        # dimensions: x(number of classes), y(number of inputs) -> each input can have own dimension
        results = np.array([np.full((len(self.formulas), len(x)), False) for x in self.inputs.values()])

        failed = False
        for idx, formula in enumerate(self.formulas):
            tree = ast.parse(formula)
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and node.id in self.inputs.keys():
                    node.id = f"self.inputs[\"{node.id}\"]"
            new_formula = ast.unparse(tree)
            try:
                result: NDArray[Any] = eval(new_formula)
                assert result.dtype == bool, "NOT A BOOL"
                results[idx] = result
            except Exception as e:
                failed = True
                print(e)
        if failed:
            raise Exception("one of the formulas does not produce booleans")

        if np.any(np.sum(results, axis=0) > 1.0):
            raise Exception("value belongs to more than one class")

        results = np.vstack([results, np.full(len(list(self.inputs.values())[0]), False)])
        for idx, col in enumerate(np.sum(results, axis=0)):
            if col == 0:
                results[-1][idx] = True

        if not np.any(results[-1]):
            results = results[:-1]

        if np.prod(np.sum(results, axis=0)) != 1.:
            raise Exception("a data entry must belong to exactly one class")

        return results
