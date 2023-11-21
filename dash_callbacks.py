from dash import callback, ctx,  Output, Input, State, ALL
from dash.exceptions import PreventUpdate
from graph_builder import GraphBuilderComponent
from mechanisms import MechanismBuilderComponent
from sliders import DistributionBuilderComponent

def setup_callbacks(
        gbc: GraphBuilderComponent,
        dbc: DistributionBuilderComponent,
        mbc: MechanismBuilderComponent
    ):
    graph_builder_component = gbc
    distribution_builder_component = dbc
    mechanism_builder_component = mbc

    @callback(
        Output("node-container", "children", allow_duplicate=True),
        Output("distribution-builder-component", "children", allow_duplicate=True),
        Output("mechanism-builder-component", "children", allow_duplicate=True),
        Input("add-node-button", "n_clicks"),
        prevent_initial_call=True
    )
    def add_new_node(_):
        print("trigger add node")
        if ctx.triggered_id == "add-node-button":
            graph_builder_component.add_node()
            distribution_builder_component.add_node()
            mechanism_builder_component.update()
        return (
            graph_builder_component.children[0].children,
            distribution_builder_component.children,
            mechanism_builder_component.children
        )

    @callback(
        Output("node-container", "children", allow_duplicate=True),
        Output("distribution-builder-component", "children", allow_duplicate=True),
        Output("mechanism-builder-component", "children", allow_duplicate=True),
        Input({"type": "rem-node", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def remove_node(x):
        print("trigger remove node")
        triggered_node = ctx.triggered_id
        triggered_node = triggered_node and triggered_node.get("index", None)
        if sum(x) > 0 and triggered_node is not None:
            graph_builder_component.remove_node(triggered_node)
            distribution_builder_component.remove_node()
            mechanism_builder_component.update()
        return (
            graph_builder_component.children[0].children,
            distribution_builder_component.children,
            mechanism_builder_component.children
        )

    @callback(
        Output("node-container", "children", allow_duplicate=True),
        Output("mechanism-builder-component", "children", allow_duplicate=True),
        State({"type": "valid-edges-add", "index": ALL}, "value"),
        Input({"type": "add-edge", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def add_new_edge(state, input):
        if sum(input) == 0:
            raise PreventUpdate

        triggered_node = ctx.triggered_id
        if triggered_node and triggered_node["type"] == "add-edge":
            source_node = triggered_node["index"]
            target_node = list(filter(lambda x: x is not None, state))
            target_node = target_node[0]
            graph_builder_component.add_edge(source_node, target_node)
            mechanism_builder_component.update()

        return (
            graph_builder_component.children[0].children,
            mechanism_builder_component.children
        )

    @callback(
        Output("node-container", "children", allow_duplicate=True),
        Output("mechanism-builder-component", "children", allow_duplicate=True),
        State({"type": "valid-edges-rem", "index": ALL}, "value"),
        Input({"type": "rem-edge", "index": ALL}, "n_clicks"),
        prevent_initial_call=True
    )
    def remove_edge(state, input):
        if sum(input) == 0:
            raise PreventUpdate

        triggered_node = ctx.triggered_id
        if triggered_node and triggered_node["type"] == "rem-edge":
            source_node = triggered_node["index"]
            target_node = list(filter(lambda x: x is not None, state))
            target_node = target_node[0] if target_node else None
            if target_node is not None:
                graph_builder_component.remove_edge(source_node, target_node)
                mechanism_builder_component.update()

        return (
            graph_builder_component.children[0].children,
            mechanism_builder_component.children
        )

    @callback(
        Output({"type": "valid-edges-add", "index": ALL}, "options"),
        Output({"type": "valid-edges-rem", "index": ALL}, "options"),
        Input("node-container", 'children')
    )
    def update_edge_dropdowns(_):
        can_be_added = []
        can_be_removed = []
        all_nodes = graph_builder_component.graph_builder.graph.keys()
        for node_i in all_nodes:
            can_be_added.append([])
            for node_j in all_nodes:
                edge = node_i, node_j
                can_add, _ = graph_builder_component.graph_builder.can_add_edge(edge)
                potential_effect = {
                    "label": node_j + (" (cycle)" if not can_add else ""),
                    "value": node_j,
                    "disabled": not can_add}
                can_be_added[-1].append(potential_effect)
            can_be_removed.append([])
            effects = graph_builder_component.graph_builder.graph.get(node_i)
            assert effects is not None, "error"
            for effect in effects:
                removable = {"label": effect, "value": effect}
                can_be_removed[-1].append(removable)

        return can_be_added, can_be_removed


    @callback(
        Output("network-graph", "elements"),
        Input("graph-view-reset", "n_clicks"),
        Input("node-container", 'children')
    )
    def update_graph(*_):
        graph = graph_builder_component.graph_builder.graph
        nodes = [
            {"data": {"id": cause, "label": cause}}
            for cause in graph.keys()
        ]
        edges = []
        for cause, effects in graph.items():
            for effect in effects:
                edges.append(
                    {"data": {"source": cause, "target": effect}}
                )
        return nodes + edges
