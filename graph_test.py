from dash import Dash, html
from dash.html.P import P
import numpy as np
import dash_cytoscape as cyto

if __name__ == "__main__":
    # x -> y -> z
    chain = np.array([
        #x, y, z
        [0, 0, 0, 0],
        [1, 0, 0, 0],
        [1, 1, 0, 0],
        [0, 0, 1, 0]
        ])

    # x <- y -> z
    fork = np.array([
        #x, y, z
        [0, 1, 0],
        [0, 0, 0],
        [0, 1, 0]
        ])

    # x -> y <- z
    collider = np.array([
        #x, y, z
        [0, 0, 0],
        [1, 0, 1],
        [0, 0, 0]
        ])

    chain_elements = []
    fork_elements = []
    collider_elements = []

    for ridx, row in enumerate(chain):
        chain_elements.append({'data': {'id': str(ridx), 'label': str(ridx)}})
        for cidx, element in enumerate(row):
            if element == 1:
                chain_elements.append({'data': {'source': str(ridx), 'target': str(cidx)}})
    for ridx, row in enumerate(fork):
        fork_elements.append({'data': {'id': str(ridx), 'label': str(ridx)}})
        for cidx, element in enumerate(row):
            if element == 1:
                fork_elements.append({'data': {'source': str(ridx), 'target': str(cidx)}})
    for ridx, row in enumerate(collider):
        collider_elements.append({'data': {'id': str(ridx), 'label': str(ridx)}})
        for cidx, element in enumerate(row):
            if element == 1:
                collider_elements.append({'data': {'source': str(ridx), 'target': str(cidx)}})


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
                             ) for elements in [chain_elements, fork_elements, collider_elements]]

    layout_div = html.Div(children=[
        html.P("Dash Cytoscape:")])
    layout_div.children.extend(graphs)


    app.layout = layout_div


    app.run_server(debug=True)
