from dash import html
from dash.dcc import RadioItems, Textarea
import dash_bootstrap_components as dbc

from models.graph import graph


class MechanismBuilder(html.Div):
    def __init__(self):
        super().__init__(id="mechanism-builder")
        self.children = []
        accordion = dbc.Accordion(always_open=True)
        accordion.children = []
        for name in graph.get_node_names():
            accordion.children.append(dbc.AccordionItem([
                MechanismContainer(name)
            ], title=name))
        self.children.append(accordion)


class MechanismContainer(html.Div):
    def __init__(self, id: str):
        super().__init__(id={"type": "mechanism-container", "index": id})
        node = graph.get_node_by_id(id)
        causes = node.get_in_node_ids()
        causes.append(f"n_{id}")
        self.children = [
            RadioItems(["Regression", "Classification"], value="Regression", id={
                "type": "mechanism-choice", "index": id
            }),
            html.Hr(),
            html.P(f"Causes: {', '.join(causes)}"),
            MechanismInput(id)
        ]



class MechanismInput(html.Div):
    def __init__(self, id: str):
        super().__init__(id={"type": "mechanism-input", "index": id})
        match graph.get_node_by_id(id).mechanism:
            case "regression":
                self.children = RegressionBuilder(id)
            case "classification":
                self.children = ClassificationBuilder(id)
            case _:
                raise Exception()


class RegressionBuilder(html.Div):
    def __init__(self, id: str):
        super().__init__(id={"type": "regression-builder", "index": id})
        node = graph.get_node_by_id(id)
        causes = node.get_in_node_ids()
        causes.append(f"n_{id}")
        self.children = [
            html.P(f"mechanism({', '.join(causes)})="),
            Textarea(id={"type": "regression-input", "index": id})
        ]


class ClassificationBuilder(html.Div):
    def __init__(self, id: str):
        super().__init__(id={"type": "classification-builder", "index": id})
        self.children = []
        self.children.append(html.P("classification: "))
        node = graph.get_node_by_id(id)
        enabled_formulas = [(c, f) for c, f in node.mechanism.formulas.items() if f.enabled]
        for c, f in enabled_formulas:
            self.children.extend([
                html.P(f"class_{c}"),
                Textarea(id={"type": "classification-input", "index": id}, value=f.text),
            ])
        self.children.append(html.P("else:"))

