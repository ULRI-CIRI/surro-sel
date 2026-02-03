"""Card UI element displaying histograms of simulated selection results.

This component allows the user to compare the outputs of various surrogate
selection strategies to statistical distributions of expected scores from
random surrogate selection, providing context for the efficacy of different
surrogate selection strategies.
"""

import plotly.express as px
from faicons import icon_svg
from shiny import module, req, ui
from shinywidgets import output_widget, render_plotly

from . import _shared


@module.ui
def hist_card():
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
def hist_card_server(input, output, session, surr, sim):
    @render_plotly
    def hist():
        req("scores" in sim())
        fig = px.histogram(
            x=sim()["scores"],
            color=sim()["ns"],
            template=_shared.PLOTLY_TEMPLATE,
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
