import dash_bootstrap_components as dbc
from dash import html
from dash.dcc import RadioItems

from models.graph import graph


class MechanismBuilder(html.Div):
    def __init__(self):
        super().__init__(id="mechanism-builder")
        self.children = []
        accordion = dbc.Accordion(start_collapsed=True)
        accordion.children = []
        for id_ in graph.get_node_ids():
            accordion.children.append(
                dbc.AccordionItem([MechanismContainer(id_)], title=id_)
            )
        self.children.append(accordion)


class MechanismContainer(html.Div):
    def __init__(self, id_: str):
        super().__init__(id={"type": "mechanism-container", "index": id_})
        node = graph.get_node_by_id(id_)
        if node is None:
            raise Exception("Node not found")

        causes = node.get_in_node_ids()
        causes.append(f"n_{id_}")

        self.children = [
            RadioItems(
                ["regression", "classification"],
                value=node.mechanism_metadata.mechanism_type,
                id={"type": "mechanism-choice", "index": id_},
            ),
            html.Hr(),
            html.P(f"Causes: {', '.join(causes)}"),
            MechanismInput(id_),
            html.Hr(),
            html.Button("confirm", id={"type": "confirm-mechanism", "index": id_})
        ]


class MechanismInput(html.Div):
    def __init__(self, id_: str):
        super().__init__(id={"type": "mechanism-input", "index": id_})
        node = graph.get_node_by_id(id_)
        if node is None:
            raise Exception("Node not found")

        match node.mechanism_metadata.mechanism_type:
            case "regression":
                self.children = RegressionBuilder(id_)
            case "classification":
                self.children = ClassificationBuilder(id_)
            case _:
                raise Exception("Invalid mechanism type found")  # type: ignore


class RegressionBuilder(html.Div):
    def __init__(self, id_: str):
        super().__init__(id={"type": "regression-builder", "index": id_})
        node = graph.get_node_by_id(id_)
        if node is None:
            raise Exception("Node not found")

        causes = node.get_in_node_ids()
        causes.append(f"n_{id_}")

        formula = node.mechanism_metadata.formulas.get("0")
        if formula is None:
            raise Exception("Formula not found")

        self.children = [
            html.P(f"mechanism({', '.join(causes)})="),
            dbc.Col(
                [
                    dbc.Row(
                        dbc.Textarea(
                            id={"type": "regression-input", "index": id_},
                            value=formula,
                            debounce=False,
                            required=True,
                        )
                    ),
                ]
            ),
        ]


class ClassificationBuilder(html.Div):
    def __init__(self, id_: str):
        super().__init__(id={"type": "classification-builder", "index": id_})
        self.children = []
        self.children.append(html.P("classification: "))
        node = graph.get_node_by_id(id_)
        if node is None:
            raise Exception("Node not found")

        for c, f in node.mechanism_metadata.get_formulas().items():
            self.children.extend(
                [
                    html.P(f"class_{c}"),
                    dbc.Col(
                        [
                            dbc.Textarea(
                                id={"type": "classification-input", "index": id_},
                                value=f,
                            ),
                            html.Button(
                                "Remove Class",
                                id={"type": "remove-class", "index": f"{id_}_{c}"},
                            ),
                        ]
                    ),
                ]
            )
        self.children.append(
            # TODO: fix this shit
            html.P("else: 'TODO -> rest that dont fit in other classes'")
        )
        self.children.append(
            html.Button("Add Class", id={"type": "add-class", "index": id_})
        )


class MechanismViewer(html.Div):
    # TODO: depending on chosen node on left -> only show
    def __init__(self):
        super().__init__(id="mechanism-viewer")
        nodes = graph.get_nodes()
        self.children = []
        for node in nodes:
            node_id = node.id_
            in_node_ids = [in_node_id for in_node_id in node.get_in_node_ids()]
            in_node_ids.append(f"n_{node_id}")
            mechanism_metadata = node.mechanism_metadata
            if mechanism_metadata.mechanism_type == "regression":
                # one formula
                # TODO: getting formulas can be None -> proper getter + check
                formula = list(mechanism_metadata.formulas.values())[0]
                assert formula is not None
                formula = f"{node_id} = f_{node_id}({', '.join(in_node_ids)}) = {formula}"
                self.children.append(html.P(formula))
            else:
                # multiple formulas
                formulas = list(mechanism_metadata.formulas.values())
                for formula in formulas:
                    if formula is not None:
                        self.children.append(html.P(formula))
            self.children.append(html.Hr())
