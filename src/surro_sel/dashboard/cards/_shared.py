"""Shared base plotly scatterplot visualization and formatting parameters.

The colorable_scatterplot() module is a reusable module for a reactive
scatterplot with optional reactive linear/log axes and indexed points that can
be recolored when global point labels are modified. It may be used, e.g., to
display a t-SNE plot of descriptors or other properties.

Additional formatting constants are provided for use in custom plotly
visualizations in other modules.
"""

from webbrowser import open_new_tab

import plotly.express as px
import plotly.graph_objects as go
from shiny import module, req
from shinywidgets import output_widget, render_widget

# Universal plotly format parameters
PLOTLY_TEMPLATE = "plotly_white"
PLOTLY_COLORS = px.colors.qualitative.Safe

# Search URL for instant data point investigation (currently PubChem)
SEARCH_URL = "https://pubchem.ncbi.nlm.nih.gov/#query=%s"
# Join string for searching multiple IDs (' OR ' for PubChem)
BATCH_SEARCH_JOIN_STR = " OR "


@module.ui
def colorable_scatterplot():
    return output_widget("plot")


@module.server
def colorable_scatterplot_server(
    input,
    output,
    session,
    data,
    labels,
    xcol,
    ycol,
    showlog,
    **layout_kwargs,
):
    # Reusable button component for log-scale axis menus
    def _log_menu_button(type, ax):
        """Reusable log-scale axis menu button component.

        Args:
            type: log or linear
            ax: x or y
        Returns:
            dict of button params
        """

        return {
            # Format strings don't work here - concatenate directly
            "label": type.capitalize() + " " + ax.upper() + "-axis",
            "method": "relayout",
            "args": [{ax.lower() + "axis.type": type.lower()}],
        }

    def _log_menu(ax):
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

    def _get_event_ids(trace, points):
        return trace["hovertext"][points.point_inds]

    def _on_click(trace, points, state):
        """Open search in a new tab when a data point is clicked."""
        if len(points.point_inds) == 1:
            # This is a cheat that works since we labeled points with the index
            open_new_tab(SEARCH_URL % _get_event_ids(trace, points)[0])

    def _on_selection(trace, points, state):
        """Open batch search in a new tab when data points are selected."""
        if len(points.point_inds) > 0:
            ids = _get_event_ids(trace, points)
            open_new_tab(SEARCH_URL % BATCH_SEARCH_JOIN_STR.join(ids))

    @render_widget
    def plot():
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
