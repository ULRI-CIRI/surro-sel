"""Parent module for qNTA SurroSel app."""

import pandas as pd
from shiny import App, reactive, render, req, ui

from . import cards, modals, sidebar, utils

# App formatting constants
NAVBAR_OPTIONS = {"class": "bg-primary", "theme": "dark"}

# Initialize the data folder and log file on app start
utils.files.update_log()

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
                # pylint: disable=E1121 # Silence errors from module calls
                cards.tsne.tsne_card("tsne"),
                cards.property.property_card("prop"),
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
                # pylint: disable=E1121 # Silence errors from module calls
                cards.hist.hist_card("hist"),
                cards.report.report_card("report"),
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
    # pylint: disable-next=E1121 # Silence error from module call
    sidebar=sidebar.dashboard_sidebar("sidebar"),
)


# Main application page server
# pylint: disable-next=C0116,W0622,W0613,R0914 # Silence server syntax errors
def server(input, output, session):
    # pylint: disable=E1120,E1121 # Silence errors from all module calls

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
    def surrogate_labels():
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

    def _set_data(data_, desc_):
        """Callback function to allow child modules to set global data.

        Args:
            data_: df containing new data
            desc_: df containing calculated descriptors
        """

        surr.set({})  # Any time data is changed, surrogates should reset
        sim.set({})

        desc.set(desc_)
        data.set(data_[data_.index.isin(desc_.index)])

    def _set_surr(surr_, sim_):
        """Callback function to allow child modules to set global surrogates.

        Args:
            surr_: dict of new surrogate selection results
            sim_: tuple of new simulated surrogate selection comparison
        """

        surr.set(surr_)
        sim.set(sim_)

    # Register server information for child modules
    modals.load.load_modal_server("load_modal", datasets=datasets, _set_data=_set_data)
    modals.upload.upload_modal_server("upload_modal", datasets=datasets, _set_data=_set_data)
    sidebar.dashboard_sidebar_server("sidebar", desc=desc, _set_surr=_set_surr)
    cards.tsne.tsne_card_server("tsne", desc, surrogate_labels)
    cards.property.property_card_server("prop", data, surrogate_labels)
    cards.hist.hist_card_server("hist", surr, sim)
    cards.report.report_card_server("report", desc, surr)

    @reactive.effect
    @reactive.file_reader(utils.files.LAST_UPDATED)
    def update_datasets():
        """Reactively update available datasets on log file change."""
        datasets.set(utils.files.get_datasets())

    @reactive.effect
    @reactive.event(input.load)
    def show_load_modal():
        """Show load modal on button click."""
        ui.modal_show(modals.load.load_modal("load_modal"))

    @reactive.effect
    @reactive.event(input.upload)
    def show_upload_modal():
        """Show upload modal on button click."""
        ui.modal_show(modals.upload.upload_modal("upload_modal"))

    @render.ui
    def no_data_alert():
        """Display an alert in place of content if no data has been loaded."""
        req(data().empty)
        return ui.card("No data found. Load data to begin.", fill=False)

    @render.ui
    def no_surr_alert():
        """Display an alert in place of content if no surrogates found."""
        req(not surr())
        return ui.card("No surrogates found. Run surrogate selection to see results.", fill=False)


# Run app
app = App(page, server)
