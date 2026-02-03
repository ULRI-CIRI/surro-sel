"""Parent module for qNTA SurroSel app."""

import pandas as pd
from shiny import App, reactive, render, req, ui

from surro_sel.components import cards, modals, sidebar
from surro_sel.utils import data_files

# App formatting constants
NAVBAR_OPTIONS = {"class": "bg-primary", "theme": "dark"}

# Initialize the data folder and log file on app start
data_files.update_log()

# Main application page UI
page = ui.page_navbar(
    ui.nav_panel(
        "",
        ui.panel_conditional(
            # If no data loaded, display an alert
            "output.no_data_alert",
            ui.output_ui("no_data_alert"),
        ),
        ui.panel_conditional(
            # If data loaded, display output content
            "!output.no_data_alert",
            ui.layout_columns(
                cards.tsne_card("tsne"),
                cards.property_card("prop"),
                max_height="50%",
            ),
        ),
        ui.panel_conditional(
            # If no surrogates found, display an alert
            "output.no_surr_alert && !output.no_data_alert",
            ui.output_ui("no_surr_alert"),
        ),
        ui.panel_conditional(
            # If surrogates found, display output content
            "!output.no_surr_alert && !output.no_data_alert",
            ui.layout_columns(
                cards.hist_card("hist"),
                cards.report_card("report"),
                max_height="50%",
            ),
        ),
    ),
    ui.nav_spacer(),
    ui.nav_control(ui.input_action_button("load", "Load Existing Data")),
    ui.nav_control(ui.input_action_button("upload", "Upload New Data")),
    title="qNTA SurroSel",
    fillable=True,
    navbar_options=ui.navbar_options(**NAVBAR_OPTIONS),
    sidebar=sidebar.dashboard_sidebar("sidebar"),
)


# Main application page server
def server(input: object, output: object, session: object) -> None:
    # Reactive value for list of available loaded dataset names
    datasets = reactive.value([])
    # Original data and calculated descriptors for current dataset
    data = reactive.value(pd.DataFrame())
    desc = reactive.value(pd.DataFrame())
    # Real surrogate selection data
    surr = reactive.value({})
    # Simulated random comparison surrogate selection data
    sim = reactive.value({})

    @reactive.calc
    def surrogate_labels() -> list:
        """Reactively convert surrogate selection data to data point labels."""

        # Initialize an empty list of labels for each point
        labels = {i: [] for i in range(desc().shape[0])}
        for strat, (idx, _) in surr().items():
            # For each in the included surrogate selection strategies...
            for i in idx:
                # ...add to the labels of all points selected by that strategy
                labels[i].append(strat)

        # Join all labels for each point into a single string
        return ["&".join(sorted(x)) if x else "none" for x in labels.values()]

    def on_data_loaded(data_: pd.DataFrame, desc_: pd.DataFrame) -> None:
        """Callback function to allow child modules to set global data.

        Args:
            data_: df containing new data
            desc_: df containing calculated descriptors
        """

        surr.set({})  # Any time data is changed, surrogates should reset
        sim.set({})

        desc.set(desc_)
        data.set(data_[data_.index.isin(desc_.index)])

    def on_surrogates_selected(surr_: dict, sim_: dict) -> None:
        """Callback function to allow child modules to set global surrogates.

        Args:
            surr_: dict of new surrogate selection results
            sim_: dict of new simulated surrogate selection comparison
        """

        surr.set(surr_)
        sim.set(sim_)

    # Register server information for child modules
    modals.load_modal_server("load_modal", datasets=datasets, on_data_loaded=on_data_loaded)
    modals.upload_modal_server("upload_modal", datasets=datasets, on_data_loaded=on_data_loaded)
    sidebar.dashboard_sidebar_server(
        "sidebar", desc=desc, on_surrogates_selected=on_surrogates_selected
    )
    cards.tsne_card_server("tsne", desc, surrogate_labels)
    cards.property_card_server("prop", data, surrogate_labels)
    cards.hist_card_server("hist", surr, sim)
    cards.report_card_server("report", desc, surr)

    @reactive.effect
    @reactive.file_reader(data_files.LAST_UPDATED)
    def update_datasets() -> None:
        """Reactively update available datasets on log file change."""
        datasets.set(data_files.get_datasets())

    @reactive.effect
    @reactive.event(input.load)
    def show_load_modal() -> None:
        """Show load modal on button click."""
        ui.modal_show(modals.load_modal("load_modal"))

    @reactive.effect
    @reactive.event(input.upload)
    def show_upload_modal() -> None:
        """Show upload modal on button click."""
        ui.modal_show(modals.upload_modal("upload_modal"))

    @render.ui
    def no_data_alert() -> ui.card:
        """Display an alert in place of content if no data has been loaded."""
        req(data().empty)
        return ui.card("No data found. Load data to begin.", fill=False)

    @render.ui
    def no_surr_alert() -> ui.card:
        """Display an alert in place of content if no surrogates found."""
        req(not surr())
        return ui.card("No surrogates found. Run surrogate selection to see results.", fill=False)


# Run app
app = App(page, server)
