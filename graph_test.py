from dash import Dash, html
from dash.html.P import P
import numpy as np
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
    # currently via adj matrix
    # since expected to be sparse -> better adj list

    # x -> y -> z
    chain = AdjecencyList([('x', 'y'), ('y', 'z'), ('z', 'a'), ('a', 'b'), ('b', 'c')])
    # x <- y -> z
    fork = AdjecencyList([('y', 'x'), ('y', 'z'), ('y', 'a')])
    # x -> y <- z
    collider = AdjecencyList([('x', 'y'), ('z', 'y'), ('a', 'y')])

    app = Dash(__name__)

    graphs = [cyto.Cytoscape(elements=elements, layout={'name': 'breadthfirst'},
                             style={'width': '400px', 'height': '500px','border': '2px black solid',
                                    'margin': '2px'},
                             stylesheet=[
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
                                         'label': 'data(id)'
                                         }

                                     }]
                             ) for elements in [chain.to_cyto(), fork.to_cyto(), collider.to_cyto()]]

    layout_div = html.Div(children=[
        html.P("Dash Cytoscape:")])
    layout_div.children.extend(graphs)


    app.layout = layout_div


    app.run_server(debug=True)
