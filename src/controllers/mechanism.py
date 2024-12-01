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
    MechanismViewer,
    VariableSelection
)

LOGGER = DashLogger(name="MechanismController", level=logging.DEBUG)


def setup_callbacks():

    @callback(
        Output("variable-selection-mechanism", "children", allow_duplicate=True),
        Output("mechanism-config", "children", allow_duplicate=True),
        Output("mechanism-viewer", "children", allow_duplicate=True),
        Input("mechanism-builder-target-node", "value"),
        prevent_initial_call=True
    )
    def select_node(selected_node_id: str):
        if selected_node_id == VariableSelection.variable:
            # this is called on startup/refresh: keep custom names
            return (
                VariableSelection().children,
                MechanismConfig().children,
                MechanismViewer().children
            )

        LOGGER.info(f"Selecting new node: {selected_node_id}")
        VariableSelection.variable = selected_node_id
        node = graph.get_node_by_id(VariableSelection.variable)
        assert node is not None
        MechanismConfig.mechanism_type = node.mechanism_metadata.mechanism_type
        MechanismConfig.is_open = False  # closed on default
        MechanismViewer.error = "invalid_formula"
        return (
            VariableSelection().children,
            MechanismConfig().children,
            MechanismViewer().children
        )

    @callback(
        Output("mechanism-config", "children", allow_duplicate=True),
        Output("variable-selection-mechanism", "children", allow_duplicate=True),
        Output("mechanism-viewer", "children", allow_duplicate=True),
        Input("mechanism-choice", "value"),
        prevent_initial_call=True
    )
    def choose_mechanism(new_mechanism: MechanismType):
        if MechanismConfig.mechanism_type == new_mechanism:
            return (
                MechanismConfig().children,
                VariableSelection().children,
                MechanismViewer().children
            )

        assert VariableSelection.variable is not None
        node = graph.get_node_by_id(VariableSelection.variable)
        assert node is not None

        LOGGER.info(f"Choosing new mechanism: {new_mechanism}")

        node.mechanism_metadata.mechanism_type = new_mechanism
        node.mechanism_metadata.reset_formulas()
        MechanismConfig.mechanism_type = new_mechanism
        MechanismConfig.is_open = False
        MechanismViewer.error = "invalid_formula"
        return (
            MechanismConfig().children,
            VariableSelection().children,
            MechanismViewer().children
        )

    @callback(
        Output("classification-builder", "children", allow_duplicate=True),
        Output("mechanism-viewer", "children", allow_duplicate=True),
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

        MechanismViewer.error = "invalid_formula"
        return (
            ClassificationBuilder().children,
            MechanismViewer().children
        )

    @callback(
        Output("classification-builder", "children", allow_duplicate=True),
        Output("mechanism-viewer", "children", allow_duplicate=True),
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

        MechanismViewer.error = "confirmation needed"
        return (
            ClassificationBuilder().children,
            MechanismViewer().children,
        )


    @callback(
        Output("mechanism-config", "children", allow_duplicate=True),
        Output("mechanism-viewer", "children", allow_duplicate=True),
        Input("confirm-classification", "n_clicks"),
        State({"type": "classification-input", "index": ALL}, "value"),
        State({"type": "classification-input", "index": ALL}, "id"),
        prevent_initial_call=True,
    )
    def confirm_classification_mechanism(clicked, classification_inputs, classification_ids):
        if not clicked:
            raise PreventUpdate()

        assert VariableSelection.variable is not None
        node = graph.get_node_by_id(VariableSelection.variable)
        assert node is not None

        classification_ids = [x["index"] for x in classification_ids]
        new_formulas = {
            c_id: c_input for c_id, c_input in zip(classification_ids, classification_inputs)
        }
        for c_id, c_input in new_formulas.items():
            node.mechanism_metadata.formulas[c_id] = c_input

        mechanism_check = node.formulas_are_valid()
        MechanismViewer.error = mechanism_check.error
        node.mechanism_metadata.valid = mechanism_check.error is None
        print(f"error: {mechanism_check.error}")

        return (
            MechanismConfig().children,
            MechanismViewer().children,
        )

    @callback(
        Output("mechanism-config", "children", allow_duplicate=True),
        Output("mechanism-viewer", "children", allow_duplicate=True),
        Input("confirm-regression", "n_clicks"),
        State("regression-input", "value"),
        prevent_initial_call=True,
    )
    def confirm_regression_mechanism(clicked, regression_input):
        if not clicked:
            raise PreventUpdate()

        assert VariableSelection.variable is not None
        node = graph.get_node_by_id(VariableSelection.variable)
        assert node is not None

        node.mechanism_metadata.formulas["0"] = regression_input
        mechanism_check = node.formulas_are_valid()
        print(mechanism_check)
        MechanismViewer.error = mechanism_check.error
        node.mechanism_metadata.valid = mechanism_check.error is None

        return (
            MechanismConfig().children,
            MechanismViewer().children,
        )

    @callback(
        Output("collapse-regression", "is_open", allow_duplicate=True),
        Input("toggle-help-regression", "n_clicks"),
        State("collapse-regression", "is_open"),
        prevent_initial_call=True,
    )
    def toggle_regression_help(clicked, is_open: bool):
        if not clicked:
            raise PreventUpdate()
        MechanismConfig.is_open = not MechanismConfig.is_open
        return MechanismConfig.is_open

    @callback(
        Output("collapse-classification", "is_open", allow_duplicate=True),
        Input("toggle-help-classification", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_classification_help(clicked):
        if not clicked:
            raise PreventUpdate()
        MechanismConfig.is_open = not MechanismConfig.is_open
        return MechanismConfig.is_open

