import logging
from typing import Literal

from dash import ALL, MATCH, Input, Output, State, callback, ctx
from dash.exceptions import PreventUpdate
from flask.app import cli

from models.graph import graph
from models.mechanism import MechanismType
from utils.logger import DashLogger
from views.mechanism import (
    ClassificationBuilder,
    MechanismConfig,
    VariableSelection
)

LOGGER = DashLogger(name="MechanismController", level=logging.DEBUG)


def setup_callbacks():

    @callback(
        Output("variable-selection-mechanism", "children", allow_duplicate=True),
        Output("mechanism-config", "children", allow_duplicate=True),
        Input("mechanism-builder-target-node", "value"),
        prevent_initial_call=True
    )
    def select_node(selected_node_id: str):
        if selected_node_id == VariableSelection.variable:
            # this is called on startup/refresh: keep custom names
            # TODO: add mechanism selection once finished
            return (
                VariableSelection().children,
                MechanismConfig().children
            )

        LOGGER.info(f"Selecting new node: {selected_node_id}")
        VariableSelection.variable = selected_node_id
        node = graph.get_node_by_id(VariableSelection.variable)
        assert node is not None
        MechanismConfig.mechanism_type = node.mechanism_metadata.mechanism_type
        return (
            VariableSelection().children,
            MechanismConfig().children
        )

    @callback(
        Output("mechanism-config", "children", allow_duplicate=True),
        Input("mechanism-choice", "value"),
        prevent_initial_call=True
    )
    def choose_mechanism(new_mechanism: MechanismType):
        if MechanismConfig.mechanism_type == new_mechanism:
            return MechanismConfig().children

        assert VariableSelection.variable is not None
        node = graph.get_node_by_id(VariableSelection.variable)
        assert node is not None

        LOGGER.info(f"Choosing new mechanism: {new_mechanism}")

        node.mechanism_metadata.mechanism_type = new_mechanism
        # TODO: not sure if reset is desired
        node.mechanism_metadata.reset_formulas()
        MechanismConfig.mechanism_type = new_mechanism
        return MechanismConfig().children

    @callback(
        Output("classification-builder", "children", allow_duplicate=True),
        Input("add-class", "n_clicks"),
        prevent_initial_call=True,
    )
    def add_class(clicked):
        if not clicked:
            raise PreventUpdate()

        LOGGER.info(f"Adding Class: {VariableSelection.variable}")

        assert VariableSelection.variable is not None
        node = graph.get_node_by_id(VariableSelection.variable)
        assert node is not None

        mechanism = node.mechanism_metadata
        if mechanism.get_next_free_class_id() is None:
            LOGGER.error("Max limit of sub classes reached")
            raise PreventUpdate

        try:
            mechanism.add_class()
        except Exception as e:
            LOGGER.exception("Failed to add class")
            raise PreventUpdate from e

        return ClassificationBuilder().children

    @callback(
        Output("classification-builder", "children", allow_duplicate=True),
        Input({"type": "remove-class", "index": ALL}, "n_clicks"),
        prevent_initial_call=True,
    )
    def remove_class(clicked):
        print(clicked)
        if not any(clicked):
            raise PreventUpdate()

        assert isinstance(ctx.triggered_id, dict)
        class_index = ctx.triggered_id.get("index")
        assert class_index is not None
        assert VariableSelection.variable is not None
        node = graph.get_node_by_id(VariableSelection.variable)
        assert node is not None

        formulas = node.mechanism_metadata.get_formulas().values()
        if len(formulas) == 1:
            raise PreventUpdate()

        try:
            node.mechanism_metadata.remove_class(class_index)
        except Exception:
            LOGGER.error("Failed to remove class")
            raise PreventUpdate()

        return ClassificationBuilder().children


    # TODO: new button for confirmation -> left and right
    def confirm_mechanism():
        raise PreventUpdate()
