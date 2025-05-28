from dash import html
import dash_bootstrap_components as dbc
from dash import dcc
from models.graph import graph


class TrainingDataSetEditor(html.Div):
    target_id: str | None = None
    training_set_counter = 0
    training_set_limit = 10
    def __init__(self):
        super().__init__(id="training-data-set-editor")
        self.style = {
            "border": "solid black 2px",
            "border-radius": "8px",
            "padding": "10px",
            "margin": "10px",
        }
        self.children = []
        if graph.data is None:
            return

        self.children.extend([
            html.H3("Define training sets:"),
            html.Hr(),
        ])
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
            html.H6("Select target variable:"),
            dcc.Dropdown(
                id="selected-target-id",
                options=node_ids,
                value=target,
                style={"border-radius": "8px"},
                searchable=False,
                clearable=False,
            ),
            html.Hr(),
            html.H6("Select source variables:"),
        ])

        options: list = [{
            "label": html.Span(node.id_ + (" (target)" if target in [node.name, node.id_] else ""), style={"padding-left": 10}),
            "value": node.id_,
            "disabled": node.id_ == target,
        } for node in nodes]

        checkbox = dcc.Checklist(
            id="selected-source-ids",
            options=options,
            value=[option.get("value") for option in options if option.get("disabled") is False]
        )
        self.children.append(checkbox)

        # button to remove training set
        self.children.extend([
            html.Hr(),
            html.Button(
                id="save-training-set",
                children="Save Training Set",
                className="one-button",
            )
        ])


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
        self.children.append(html.H3("Configured data sets:"))

        for idx, data_set in enumerate(graph.data_sets):
            row = dbc.Row([
                dbc.Col(dcc.Markdown(f"$$sources: {{{', '.join(data_set['s'])}}}$$", mathjax=True)),
                dbc.Col(dcc.Markdown(f"$$target: {data_set['t']}$$", mathjax=True)),
                dbc.Col(dcc.Markdown(f"$${data_set['m']}$$", mathjax=True)),
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
