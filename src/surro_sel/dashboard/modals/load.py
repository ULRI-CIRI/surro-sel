"""Modal containing existing dataset load functionality.

This module contains definitions for a modal allowing users to reload an
existing dataset (previously uploaded and stored as a parquet file).
"""

from shiny import module, reactive, render, ui

from ..utils import files, notifications


@module.ui
def load_modal():
    return ui.modal(
        ui.output_ui("name_select"),
        title="Load Existing Dataset",
        easy_close=False,
        footer=[ui.input_task_button("load", "Load"), ui.modal_button("Close")],
    )


@module.server
def load_modal_server(input, output, session, datasets, _set_data):
    @reactive.effect
    @reactive.event(input.load)
    def load():
        """Perform data load on button click."""

        # Show an error if button clicked without a selection
        if not input.name():
            notifications.error_notification(notifications.ValidationErrors.NO_NAME)
            return  # Stop processing, but leave the modal open

        # Otherwise, read data files and update global app data
        data, desc = files.load_data(input.name())
        _set_data(data, desc)

        # Show success notification
        notifications.load_success_notification(data.shape[0], desc.shape[0])

        # Close modal
        ui.modal_remove()

    @render.ui
    def name_select():
        return ui.input_select("name", "Dataset Name", choices=["", *datasets()])
