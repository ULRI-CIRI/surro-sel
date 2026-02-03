"""Define config and utility functions for file system interactions."""

from datetime import datetime
from pathlib import Path

import pandas as pd

# Constants for data file names
DATA_FILENAME = "data.parquet"
DESC_FILENAME = "desc.parquet"

# Locate data persistence folder and last updated log file
DATA_FOLDER = Path(__file__).parent.parent.parent / "data"
LAST_UPDATED = DATA_FOLDER / "last_updated.txt"


def get_datasets() -> list:
    """List available dataset names from data folder."""
    return [p for p in DATA_FOLDER.iterdir() if p.is_dir()]


def update_log() -> None:
    """Update last updated log file with current timestamp."""

    # Ensure data folder exists
    if not DATA_FOLDER.exists():
        DATA_FOLDER.mkdir(parents=True, exist_ok=True)

    # Write the current timestamp to the last updated file
    with open(LAST_UPDATED, "w", encoding="utf-8") as last_updated_file:
        last_updated_file.write(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def load_data(name: str) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Read data and descriptor files from a specified data directory.

    Args:
        name: name of the dataset directory to read from
    Returns:
        tuple of dfs containing original data and calculated descriptors
    """

    read_from_folder = DATA_FOLDER / name
    return (
        pd.read_parquet(read_from_folder / DATA_FILENAME),
        pd.read_parquet(read_from_folder / DESC_FILENAME),
    )


def save_data(name: str, data: pd.DataFrame, desc: pd.DataFrame) -> None:
    """Save data and descriptor files to a specified data directory.

    Args:
        name: dataset name to create directory
        data: original data df
        desc: calculated descriptor df
    """

    # Identify new data directory location and create it
    save_to_folder = DATA_FOLDER / name
    # exist_ok = False by default, throws FileExistsError
    # This will prevent overwriting any existing dataset if validation fails
    save_to_folder.mkdir(parents=True)

    data.to_parquet(save_to_folder / DATA_FILENAME, index=True)
    desc.to_parquet(save_to_folder / DESC_FILENAME, index=True)

    update_log()  # Update the last updated log
