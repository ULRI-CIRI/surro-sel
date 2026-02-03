"""Card UI element displaying a t-SNE plot of ionization efficiency."""

from shiny import module, reactive, ui

from . import _shared


@module.ui
def tsne_card():
    return ui.card(
        ui.card_header("Ionization Efficiency t-SNE"),
        ui.card_body(_shared.colorable_scatterplot("plot")),
        full_screen=True,
    )


@module.server
def tsne_card_server(input, output, session, desc, labels):
    def _make_constant_reactive(cnst):
        return reactive.calc(lambda: cnst)

    _shared.colorable_scatterplot_server(
        "plot",
        desc,
        labels,
        _make_constant_reactive("TSNE1"),
        _make_constant_reactive("TSNE2"),
        showlog=False,
        legend_title="Surrogate Set",
    )
