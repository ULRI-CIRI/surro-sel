"""Define content and config for reusable pop-up notifications to the user."""

from enum import StrEnum, auto

from shiny.ui import notification_show

DEFAULT_DURATION = 3
DEFAULT_TYPE = "message"
LOAD_SUCCESS_MESSAGE = "Successfully loaded {n_records} records ({n_structs} structurable)."


class ValidationErrors(StrEnum):
    """Enum for application form validation error types."""

    NO_NAME = auto()
    NAME_LEN = auto()
    NAME_INVALID = auto()
    NAME_DUP = auto()
    NO_FILE = auto()
    FILE_INVALID = auto()
    COLS_DUP = auto()
    NO_STRAT = auto()
    N_INVALID = auto()
    NO_USER = auto()
    NO_DATA = auto()


ERROR_MESSAGES = {
    ValidationErrors.NO_NAME: "Dataset name is required.",
    ValidationErrors.NAME_INVALID: (
        "Invalid dataset name: must have at "
        "least two chars, no more than 32 chars, and contain only "
        "alphanumerics, underscores, dashes, and spaces."
    ),
    ValidationErrors.NAME_DUP: "Dataset name already in use.",
    ValidationErrors.NO_FILE: "Data file is missing, empty, or unparsable.",
    ValidationErrors.FILE_INVALID: "Data file could not be parsed.",
    ValidationErrors.COLS_DUP: (
        "Primary ID and QSAR-ready SMILES column selections may not be the same."
    ),
    ValidationErrors.NO_STRAT: (
        "At least one surrogate selection strategy is required for automated selection."
    ),
    ValidationErrors.N_INVALID: "A valid number of surrogates is required for automated selection.",
    ValidationErrors.NO_USER: "No user selected surrogates found.",
    ValidationErrors.NO_DATA: "No data loaded for surrogate selection.",
}


def _notification(message: str, type: str = DEFAULT_TYPE) -> None:
    # Generic notification function with a specified type and default duration
    notification_show(message, type=type, duration=DEFAULT_DURATION)


def load_success_notification(n_records: int, n_structs: int) -> None:
    """Display a notification for successful data load.

    Args:
        n_records: total number of records loaded
        n_structs: number of loaded records with structures
    """

    _notification(LOAD_SUCCESS_MESSAGE.format(n_records=n_records, n_structs=n_structs))


def error_notification(key: ValidationErrors) -> None:
    """Display an error notification based on key.

    Args:
        key: dictionary key (from ValidationErrors enum) for error type
    """

    _notification(ERROR_MESSAGES[key], type="error")
