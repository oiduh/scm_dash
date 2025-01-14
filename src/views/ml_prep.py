from dash import html
import dash_bootstrap_components as dbc
from dash import dcc
from models.graph import graph


class TrainingDataSetEditor(html.Div):
    def __init__(self):
        super().__init__(id="training-data-set-editor")
        self.children = []

        # button to remove training set
        self.children.append(html.Button(
            id="remove-training-data-set", children="Remove Training Set"
        ))
        nodes = graph.get_nodes()
        assert len(nodes) > 0
        target = graph.get_node_ids()[0]
        sources = set(graph.get_node_ids())
        sources.discard(target)
        sources = list(sources) 

        node_ids = [node.name or node.id_ for node in nodes]
        self.children.extend([
            html.P("select the target variable:"),
            dcc.Dropdown(
                options=node_ids,
                value=node_ids[0]
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
                        disabled=node.id_ not in sources,
                        value=node.id_ in sources,
                    ),
                ]),
                dbc.InputGroupText(text)
            ], className="mb-3", size="lg"))
        self.children.append(dbc.Card(cardbody))


class MLPreparation(html.Div):
    def __init__(self):
        super().__init__(id="ml-preparation")
        self.children = []
        self.children.append(html.Button(
            id="add-training-set", children="Add Training Set +"
        ))
        self.children.append(TrainingDataSetEditor())




        # TODO:

        """
            start with sample training data set
            button to add new training data
            per default all variables are selected and first node is target node
            check boxes for each variable (multiple choice)
            check box for target variable (single choice)
            support multiple training sets
            left:
                add button
                edit window for currently selected set
                save button
            right:
                preview for all training sets + extra stuff e.g. data distribution
        """

