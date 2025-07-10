from models.graph import graph
from dash import Input, Output, callback, ctx
from dash.exceptions import PreventUpdate

from models.noise import DEFAULT_VARIABLES, GLOBAL_VARIABLES
from utils.logger import DashLogger
from views.graph import (
    GraphBuilder,
    GraphUploader,
    GraphViewer,
    VariableSelection as VariableSelectionGraph,
    VariableConfig,
    GeneralGraphConfig,
)
from views.lock_data import LockDataBuilder
from views.ml_lock import MLLockBuilder
from views.noise import (
    VariableSelection as VariableSelectionNoise
)
from views.mechanism import (
    MechanismConfig,
    VariableSelection as VariableSelectionMechanism,
)


LOGGER = DashLogger(name="Main-Controller")


def setup_callbacks() -> None:
    @callback(
        Output("general-graph-config", "children", allow_duplicate=True),
        Output("variable-selection-graph", "children", allow_duplicate=True),
        Output("variable-config-graph", "children", allow_duplicate=True),
        Output("network-graph", "elements", allow_duplicate=True),
        Output("variable-selection-noise", "children", allow_duplicate=True),
        Output("mechanism-config", "children", allow_duplicate=True),
        Output("data-generation-builder", "children", allow_duplicate=True),
        Output("ml-lock-builder", "children", allow_duplicate=True),
        Output("tab1", "disabled"),
        Output("tab2", "disabled"),
        Output("tab3", "disabled"),
        Output("tab4", "disabled"),
        Output("tab5", "disabled"),
        Output("tab6", "disabled"),
        Output("tab7", "disabled"),
        Output("tab8", "disabled"),
        Output("tabs", "value"),
        Input("global-reset-button", "n_clicks"),
        prevent_initial_call=True
    )
    def reset_graph(clicked):
        if not clicked:
            raise PreventUpdate()

        if ctx.triggered_id != "global-reset-button":
            raise PreventUpdate()

        global graph
        graph.reset()

        # graph view resets
        GraphUploader.last_uploaded_graph = None
        VariableSelectionGraph.selected_node_id = graph.get_node_ids()[0]
        GraphViewer.LAYOUT = GraphViewer.Layouts.circle

        # noise view resets
        VariableSelectionNoise.variable = graph.get_node_ids()[0]
        VariableSelectionNoise.sub_variable = "0"

        # mechanism view resets
        VariableSelectionMechanism.variable = graph.get_node_ids()[0]
        MechanismConfig.mechanism_type = "regression"
        MechanismConfig.is_open = False

        # lock data view resets
        LockDataBuilder.is_locked = False
        LockDataBuilder.data_generated = False

        # reset global variables
        GLOBAL_VARIABLES.SEED = DEFAULT_VARIABLES.SEED
        GLOBAL_VARIABLES.NR_DATA_POINTS = DEFAULT_VARIABLES.NR_DATA_POINTS

        LOGGER.info("Global reset button triggered. Resetting to initial setup")
        return (
            GeneralGraphConfig().children,
            VariableSelectionGraph().children,
            VariableSelectionNoise().children,
            GraphBuilder.get_graph_data(),
            VariableSelectionMechanism().children,
            VariableConfig().children,
            LockDataBuilder().children,
            MLLockBuilder().children,
            False,
            False,
            False,
            False,
            True,
            True,
            True,
            True,
            "tab-1",
        )
