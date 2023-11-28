from dash import MATCH, Input, Output, callback, html, State, ctx
from dash.exceptions import PreventUpdate
from graph_builder import graph_builder_component
from dash.dcc import Input as InputField


class MechanismContainer(html.Div):
    def __init__(self, id, node, edges):
        super().__init__(id=id)
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }
        self.children = []
        self.children.append(html.Label(f"variable: {node}"))
        self.children.append(html.Hr())
        self.children.append(html.P("affected by: "+", ".join(list(edges))))
        self.children.extend([
            html.Label(f"f({', '.join(sorted(list(edges)))}) = "),
            InputField(
                value="",
                id={"type": "formula-field", "index": node},
                type="text"
            ),
            html.Button(
                "verify",
                id={"type": "verify-formula", "index": node}
            ),
            html.P(
                "not verified",
                id={"type": "formula-validity", "index": node},
                style={
                    "border": "2px yellow solid",
                    "margin": "2px",
                }
            )
        ])


class MechanismBuilderComponent(html.Div):
    def __init__(self, id):
        super().__init__(id=id)
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }
        self.graph_builder = graph_builder_component.graph_builder
        self.update()

    def update(self):
        self.children = []


        for node, causes in self.graph_builder.graph_tracker.in_edges.items():
            self.children.append(
                MechanismContainer(
                    id={"type": "mechanism-container", "index": node},
                    node=node, edges=causes
                )
            )


mechanism_builder_component = MechanismBuilderComponent(
    id="mechanism-builder-component"
)

@callback(
    Output({"type": "formula-validity", "index": MATCH}, "style"),
    Output({"type": "formula-validity", "index": MATCH}, "children"),
    Input({"type": "verify-formula", "index": MATCH}, "n_clicks"),
    State({"type": "formula-field", "index": MATCH}, "value"),
    prevent_initial_call=True
)
def verify(_, input_formula: str):
    triggered_id = ctx.triggered_id
    if not triggered_id:
        raise PreventUpdate

    variable = triggered_id.get("index")
    assert variable, "error"


    print(f"{variable=}")
    print(f"{input_formula=}")
    if not input_formula:
        return(
            {
                "border": "2px yellow solid",
                "margin": "2px",
            },
            "no formula"
        )
    elif input_formula.isdigit():
        return(
            {
                "border": "2px green solid",
                "margin": "2px",
            },
            "valid formula"
        )
    else:
        return(
            {
                "border": "2px red solid",
                "margin": "2px",
            },
            "invalid formula"
        )

