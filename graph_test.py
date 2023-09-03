from dash import Dash, html
import dash_cytoscape as cyto
from typing import List, Tuple

class AdjecencyList:
    def __init__(self, input: List[Tuple[str, str]]) -> None:
        self.nodes = set()
        self.edges: List[Tuple[str, str]] = []
        for src, tgt in input:
            self.nodes.add(tgt)
            self.nodes.add(src)
            self.edges.append((tgt, src))

    def to_cyto(self):
        elements = []
        for node in self.nodes:
            elements.append({'data': {'id': node, 'label': node}})
        for tgt, src in self.edges:
            elements.append({'data': {'source': tgt, 'target': src}})
        return elements



if __name__ == "__main__":
    # x -> y -> z
    chain = AdjecencyList([('x', 'y'), ('y', 'z'), ('z', 'a'), ('a', 'b'), ('b', 'c')])
    # x <- y -> z
    fork = AdjecencyList([('y', 'x'), ('y', 'z'), ('y', 'a')])
    # x -> y <- z
    collider = AdjecencyList([('x', 'y'), ('z', 'y'), ('a', 'y')])

    app = Dash(__name__)

    graphs: List[cyto.Cytoscape] = []
    for adj_list in [chain, fork, collider]:
        elements = adj_list.to_cyto()
        style = {
            'width': '400px', 'height': '500px',
            'border': '2px black solid',
            'margin': '2px'
        }
        layout = {'name': 'breadthfirst'}
        stylesheet = [
            {
                'selector': 'edge',
                'style': {
                    'curve-style': 'bezier',
                    'source-arrow-shape': 'triangle'
                }
            },
            {
                'selector': 'node',
                'style': {
                    'label': 'data(id)',
                }
            }
        ]

        graphs.append(cyto.Cytoscape(
            elements=elements,
            style=style,
            layout=layout,
            stylesheet=stylesheet
        ))

    layout_div = html.Div()
    layout_div.children = []
    layout_div.children.extend(graphs)

    app.layout = layout_div

    app.run_server(debug=True)
