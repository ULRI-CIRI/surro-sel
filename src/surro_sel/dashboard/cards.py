"""Card UI elements for dashboard visualization and reporting.

This module consolidates all card components including:
- tsne_card: t-SNE plot of ionization efficiency
- hist_card: histogram of LARD score distributions
- property_card: scatterplot of user selected properties
- report_card: text report of surrogate selection results
- colorable_scatterplot: reusable scatterplot with reactive coloring
"""

from webbrowser import open_new_tab

import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from faicons import icon_svg
from shiny import module, reactive, render, req, ui
from shinywidgets import output_widget, render_plotly, render_widget

# Universal plotly format parameters
PLOTLY_TEMPLATE = "plotly_white"
PLOTLY_COLORS = px.colors.qualitative.Safe

# Search URL for instant data point investigation (currently PubChem)
SEARCH_URL = "https://pubchem.ncbi.nlm.nih.gov/#query=%s"
# Join string for searching multiple IDs (' OR ' for PubChem)
BATCH_SEARCH_JOIN_STR = " OR "


# ============================================================================
# Shared Colorable Scatterplot Component
# ============================================================================


@module.ui
def colorable_scatterplot() -> object:
    return output_widget("plot")


@module.server
def colorable_scatterplot_server(
    input: object,
    output: object,
    session: object,
    data: object,
    labels: object,
    xcol: object,
    ycol: object,
    showlog: bool,
    **layout_kwargs,
) -> None:
    """Server logic for reusable colorable scatterplot component."""

    # Reusable button component for log-scale axis menus
    def _log_menu_button(type: str, ax: str) -> dict:
        """Reusable log-scale axis menu button component.

        Args:
            type: log or linear
            ax: x or y
        Returns:
            dict of button params
        """

        return {
            # Format strings don't work here - concatenate directly
            "label": f"{type.capitalize()} {ax.upper()}-axis",
            "method": "relayout",
            "args": [{f"{ax.lower()}axis.type": type.lower()}],
        }

    def _log_menu(ax: str) -> dict:
        """Reusable log-scale axis menu component.

        Args:
            ax: x or y
        Returns:
            dict of menu params
        """

        # Set menu location depending on x or y axis
        loc = (
            {"y": 0, "x": 1.05, "yanchor": "bottom", "xanchor": "left", "direction": "up"}
            if ax.lower() == "x"
            else {"y": 1.05, "x": 0, "yanchor": "bottom", "xanchor": "left", "direction": "down"}
        )

        # Create menu with buttons and location params
        return {
            "showactive": True,
            "type": "dropdown",
            "buttons": [_log_menu_button("linear", ax), _log_menu_button("log", ax)],
        } | loc

    def _get_event_ids(trace: dict, points: object) -> list:
        return trace["hovertext"][points.point_inds]

    def _on_click(trace: dict, points: object, state: object) -> None:
        """Open search in a new tab when a data point is clicked."""
        if len(points.point_inds) == 1:
            # This is a cheat that works since we labeled points with the index
            open_new_tab(SEARCH_URL % _get_event_ids(trace, points)[0])

    def _on_selection(trace: dict, points: object, state: object) -> None:
        """Open batch search in a new tab when data points are selected."""
        if len(points.point_inds) > 0:
            ids = _get_event_ids(trace, points)
            open_new_tab(SEARCH_URL % BATCH_SEARCH_JOIN_STR.join(ids))

    @render_widget
    def plot() -> object:
        """Build the main figure widget component for the plot."""
        req(xcol() and ycol() and not data().empty)

        # Show or hide log-scale axis menus
        menus = [_log_menu("x"), _log_menu("y")] if showlog else []

        # Build the base figure
        fig = px.scatter(
            data(),
            x=xcol(),
            y=ycol(),
            color=labels(),
            # Required for point indexing
            # Display only, not currently functional
            hover_name=data().index,
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=PLOTLY_COLORS,
        ).update_layout(updatemenus=menus, **layout_kwargs)

        # Set up the figure widget to register click handler
        widg = go.FigureWidget(fig.data, fig.layout)
        for tr in widg.data:
            tr.on_click(_on_click)
            tr.on_selection(_on_selection)

        return widg


# ============================================================================
# Report Card Component
# ============================================================================


@module.ui
def report_card() -> ui.card:
    return ui.card(
        ui.card_header("Surrogate Selection Report"),
        ui.card_body(ui.output_text_verbatim("report")),
    )


@module.server
def report_card_server(
    input: object, output: object, session: object, desc: object, surr: object
) -> None:
    """Server logic for surrogate selection report card."""

    @render.text
    def report() -> str:
        req(surr())
        return "\n====================\n".join(
            [
                f"{strat.upper()}\nLARD: {float(res[1]):.3g}\n"
                f"Surrogates Selected:\n{chr(10).join(desc().index[res[0]])}"
                for strat, res in surr().items()
            ]
        )


# ============================================================================
# Histogram Card Component
# ============================================================================


@module.ui
def hist_card() -> ui.card:
    return ui.card(
        ui.card_header(
            ui.span(
                "LARD Score Distribution ",
                ui.tooltip(
                    icon_svg("circle-info"),
                    (
                        "Distributions represent expected scores from random "
                        "selection at the same surrogate set size as well as "
                        "reference sizes of 1, 10, 20, and 50% of the total "
                        "data set size."
                    ),
                    placement="right",
                ),
            )
        ),
        output_widget("hist"),
        full_screen=True,
    )


@module.server
def hist_card_server(
    input: object, output: object, session: object, surr: object, sim: object
) -> None:
    """Server logic for LARD score histogram card."""

    @render_plotly
    def hist() -> object:
        req("scores" in sim())
        fig = px.histogram(
            x=sim()["scores"],
            color=sim()["ns"],
            template=PLOTLY_TEMPLATE,
            color_discrete_sequence=px.colors.sequential.Greys_r,
            nbins=100,
            opacity=0.6,
            barmode="overlay",
        ).update_layout(
            xaxis_title="Leveraged Averaged Representative Distance (LARD)",
            yaxis_title="Count",
            legend_title="Surrogate Set Size",
        )

        sort_surr = sorted(surr().items(), key=lambda x: x[1][1])
        for i, (strat, results) in enumerate(sort_surr):
            fig.add_vline(
                x=results[1],
                line_width=2,
                line_dash="dash",
                line_color="black",
                annotation_text=f"{strat} (N={len(results[0])})",
                annotation_position="bottom right" if i % 2 else "top right",
                annotation_bgcolor="rgba(255, 255, 255, 0.75)",
                annotation_xshift=2,
                opacity=1,
            )

        return fig


# ============================================================================
# t-SNE Card Component
# ============================================================================


@module.ui
def tsne_card() -> ui.card:
    return ui.card(
        ui.card_header("Ionization Efficiency t-SNE"),
        ui.card_body(colorable_scatterplot("plot")),
        full_screen=True,
    )


@module.server
def tsne_card_server(
    input: object, output: object, session: object, desc: object, labels: object
) -> None:
    """Server logic for t-SNE visualization card."""

    def _make_constant_reactive(cnst: str) -> reactive.Calc:
        return reactive.calc(lambda: cnst)

    colorable_scatterplot_server(
        "plot",
        desc,
        labels,
        _make_constant_reactive("TSNE1"),
        _make_constant_reactive("TSNE2"),
        showlog=False,
        legend_title="Surrogate Set",
    )


# ============================================================================
# Property Comparison Card Component
# ============================================================================


@module.ui
def property_card() -> ui.card:
    return ui.card(
        ui.card_header("Property Comparison Plot"),
        ui.card_body(
            ui.layout_column_wrap(ui.output_ui("xcol_select"), ui.output_ui("ycol_select")),
            colorable_scatterplot("plot"),
        ),
        full_screen=True,
    )


@module.server
def property_card_server(
    input: object, output: object, session: object, data: object, labels: object
) -> None:
    """Server logic for property comparison card."""

    @reactive.calc
    def num_cols() -> list:
        """Reactive calculation of numerical columns in input data."""
        return data().select_dtypes(include=np.number).columns.tolist()

    def _num_cols_select(ax: str) -> ui.Select:
        return ui.input_select(
            ax.lower() + "col", ax.upper() + "-axis Property", choices=num_cols()
        )

    @render.ui
    def xcol_select() -> ui.Select:
        return _num_cols_select("x")

    @render.ui
    def ycol_select() -> ui.Select:
        return _num_cols_select("y")

    colorable_scatterplot_server(
        "plot", data, labels, input.xcol, input.ycol, showlog=True, legend_title="Surrogate Set"
    )
