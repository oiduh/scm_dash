from dash import html


class Placeholder(html.Div):
    def __init__(self, id: str):
        super().__init__(id=id)
        self.children = "PLACEHOLDER"
        self.style = {
            "border": "3px red solid",
            "margin": "3px",
        }
