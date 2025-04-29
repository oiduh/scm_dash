from dash import html
import dash_bootstrap_components as dbc
from dash import dcc
from models.graph import graph


class TrainingDataSetEditor(html.Div):
    active: bool = False
    target_id: str | None = None
    def __init__(self):
        super().__init__(id="training-data-set-editor")
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }
        self.children = []
        if TrainingDataSetEditor.active is False:
            return

        # button to remove training set
        self.children.append(dbc.Row([
            dbc.Col(html.Button(
                id="save-training-set",
                children="Save Training Set",
                className="one-button",
            )),
            dbc.Col(html.Button(
                id="remove-training-set",
                children="Remove Training Set",
                className="one-button",
            )),
        ]))
        nodes = graph.get_nodes()
        node_ids = [node.name or node.id_ for node in nodes]
        assert len(nodes) > 0
        if TrainingDataSetEditor.target_id is None:
            target = graph.get_node_ids()[0]
        else:
            target = TrainingDataSetEditor.target_id
        sources = set(graph.get_node_ids())
        sources.discard(target)
        sources = list(sources)

        # TODO: add field for optional intervention -> simple float number input

        self.children.extend([
            html.P("select the target variable:"),
            dcc.Dropdown(
                id="selected-target-id",
                options=node_ids,
                value=target,
                style={"border-radius": "8px"},
            ),
            html.Hr(),
            html.P("select the source variables:"),
        ])

        cardbody = dbc.CardBody()
        cardbody.children = []
        for node in nodes:
            text = node.name or node.id_
            if node.id_ == target:
                text += " (target)"
            cardbody.children.append(dbc.InputGroup([
                dbc.InputGroupText([
                    dbc.Checkbox(
                        id={"type": "selected-source-id", "index": node.id_},
                        disabled=node.id_==target,
                        value=node.id_ in sources,
                    ),
                ]),
                dbc.InputGroupText(text)
            ], className="mb-3", size="lg"))
        self.children.append(dbc.Card(cardbody))


class MLPreparation(html.Div):
    training_set_counter = 0
    training_set_limit = 10
    def __init__(self):
        super().__init__(id="ml-preparation")
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }
        self.children = []
        self.children.append(html.Button(
            id="add-training-set",
            children="Add Training Set +",
            className="one-button",
        ))
        self.children.append(TrainingDataSetEditor())


class MLViewer(html.Div):
    def __init__(self):
        super().__init__(id="ml-viewer")
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }
        self.children = []

        for idx, data_set in enumerate(graph.data_sets):
            row = dbc.Row([
                dbc.Col(html.P(f"sources: {data_set['s']}")),
                dbc.Col(html.P(f"target: {data_set['t']}")),
                dbc.Col(html.Button(
                    "remove",
                    id={
                        "type": "remove-data-set",
                        "index": str(idx)
                    },
                    className="one-button",
                )),
            ])
            self.children.append(row)
