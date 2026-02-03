"""Card UI element displaying a scatterplot of user selected properties."""

import numpy as np
from shiny import module, reactive, render, ui

from . import _shared


@module.ui
def property_card():
    return ui.card(
        ui.card_header("Property Comparison Plot"),
        ui.card_body(
            ui.layout_column_wrap(ui.output_ui("xcol_select"), ui.output_ui("ycol_select")),
            _shared.colorable_scatterplot("plot"),
        ),
        full_screen=True,
    )


@module.server
def property_card_server(input, output, session, data, labels):
    @reactive.calc
    def num_cols():
        """Reactive calculation of numerical columns in input data."""
        return data().select_dtypes(include=np.number).columns.tolist()

    def _num_cols_select(ax):
        return ui.input_select(
            ax.lower() + "col", ax.upper() + "-axis Property", choices=num_cols()
        )

    @render.ui
    def xcol_select():
        return _num_cols_select("x")

    @render.ui
    def ycol_select():
        return _num_cols_select("y")

    _shared.colorable_scatterplot_server(
        "plot", data, labels, input.xcol, input.ycol, showlog=True, legend_title="Surrogate Set"
    )
