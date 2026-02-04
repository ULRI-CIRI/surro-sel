"""Parent module for qNTA SurroSel app."""

from shiny import App, reactive, render, req, ui

from components import cards, data_store, modals, sidebar
from utils import data_files

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
    ui.nav_control(
        ui.tooltip(ui.input_action_button("test_btn", "Did GitHub/Posit CI/CD work?"), "Yep!")
    ),
    ui.nav_control(ui.input_action_button("load", "Load Existing Data")),
    ui.nav_control(ui.input_action_button("upload", "Upload New Data")),
    title="qNTA SurroSel",
    fillable=True,
    navbar_options=ui.navbar_options(**NAVBAR_OPTIONS),
    sidebar=sidebar.dashboard_sidebar("sidebar"),
)


# Main application page server
def server(input: object, output: object, session: object) -> None:
    # Central app state store
    store = data_store.DataStore()
    # Reactive value for list of available loaded dataset names
    datasets = reactive.value([])

    # Register child modules
    modals.load_modal_server("load_modal", datasets=datasets, on_data_loaded=store.update_data)
    modals.upload_modal_server("upload_modal", datasets=datasets, on_data_loaded=store.update_data)
    sidebar.dashboard_sidebar_server(
        "sidebar", desc=store.desc, on_surrogates_selected=store.update_surrogates
    )
    cards.tsne_card_server("tsne", store.desc, store.surrogate_labels)
    cards.property_card_server("prop", store.data, store.surrogate_labels)
    cards.hist_card_server("hist", store.surr, store.sim)
    cards.report_card_server("report", store.desc, store.surr)

    # File system monitoring
    @reactive.effect
    @reactive.file_reader(data_files.LAST_UPDATED)
    def update_datasets() -> None:
        """Reactively update available datasets on log file change."""
        datasets.set(data_files.get_datasets())

    # Modal show handlers
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

    # Reactive state queries for conditionals
    # These must directly access reactive values to establish proper dependencies
    @reactive.calc
    def data_ready() -> bool:
        """Reactive computation of data loaded state."""
        return not store.desc().empty

    @reactive.calc
    def surrogates_ready() -> bool:
        """Reactive computation of surrogate selected state."""
        return bool(store.surr())

    # Conditional UI panel rendering
    @render.ui
    def no_data_alert() -> ui.card:
        """Display an alert in place of content if no data has been loaded."""
        req(not data_ready())
        return ui.card("No data found. Load data to begin.", fill=False)

    @render.ui
    def no_surr_alert() -> ui.card:
        """Display an alert in place of content if no surrogates found."""
        req(not surrogates_ready())
        return ui.card("No surrogates found. Run surrogate selection to see results.", fill=False)


# Run app
app = App(page, server)
