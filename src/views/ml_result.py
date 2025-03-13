from dash import html, dcc, dash_table
import dash_bootstrap_components as dbc
from models.graph import graph
from models.ml import Classification, Regression

class MLResultViewer(html.Div):
    def __init__(self):
        super().__init__(id="ml-result-viewer")
        self.children = []
        self.style = {
            "width": "80%",
            "margin-inline": "auto",
            "border": "1px solid black"
        }

        if len(graph.data_sets) < 1:
            return
        for data_set in graph.data_sets:
            row = dbc.Row()
            row.children = []
            sources = data_set["s"]
            assert isinstance(sources, list)
            target = data_set["t"]
            assert isinstance(target, str)
            data = graph.data
            assert data is not None
            target_node = graph.get_node_by_id(target)
            assert target_node is not None
            if target_node.mechanism_metadata.mechanism_type == "regression":
                scores = Regression().evaluate_models(
                    data=data,
                    sources=sources,
                    target=target,
                )
            else:
                scores = Classification().evaluate_models(
                    data=data,
                    sources=sources,
                    target=target,
                )
                # TODO:also include semi supervised learning once this looks ok
            row.children.append(html.P(f"source(s): {', '.join(sources)}"))
            row.children.append(html.P(f"targert: {target}"))
            row.children.append(dash_table.DataTable(
                scores.to_dict("records"), 
                [{"name": i, "id": i} for i in scores.columns]
            ))
            self.children.append(row)
