from dash import html
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
            InputField(type="text"),
            html.Button("verify")
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
        causes = {node: set() for node in self.graph_builder.graph.keys()}
        for node, edges in self.graph_builder.graph.items():
            # TODO: fix potential error
            m = causes.get(node)
            assert m is not None, "error"
            m.add(f"n_{node}")
            causes.update({node: m})
            for x in edges:
                m = causes.get(x)
                assert m is not None, "error"
                m.add(node)
                causes.update({x: m})


        print(causes)

        for node, causes in causes.items():
            self.children.append(
                MechanismContainer(
                    id={"type": "mechanism-container", "index": node},
                    node=node, edges=causes
                )
            )


mechanism_builder_component = MechanismBuilderComponent(
    id="mechanism-builder-component"
)

