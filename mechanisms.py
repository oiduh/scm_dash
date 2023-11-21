from dash import html
from graph_builder import graph_builder_component


class MechanismContainer(html.Div):
    def __init__(self, id, node, edges):
        super().__init__(id=id)
        self.style = {
            "border": "2px black solid",
            "margin": "2px",
        }
        self.children = []
        self.children.append(html.Label(node))
        self.children.append(html.Hr())
        self.children.append(html.P(", ".join(list(edges))))


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
        for node, edges in self.graph_builder.graph.items():
            self.children.append(
                MechanismContainer(
                    id={"type": "mechanism-container", "index": node},
                    node=node, edges=edges
                )
            )


mechanism_builder_component = MechanismBuilderComponent(
    id="mechanism-builder-component"
)

