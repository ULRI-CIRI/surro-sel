"""Centralized reactive data store for application state management.

This module provides a DataStore class that manages all application state
reactively and provides a clean API for state mutations. This encapsulation
simplifies testing, debugging, and future enhancements.
"""

import pandas as pd
from shiny import reactive


class DataStore:
    """Centralized store for all data and surrogate state.

    This class encapsulates reactive state management for data,
    descriptors, and surrogate selections.
    """

    def __init__(self) -> None:
        """Initialize empty store with reactive values."""
        self.data = reactive.value(pd.DataFrame())
        self.desc = reactive.value(pd.DataFrame())
        self.surr = reactive.value({})
        self.sim = reactive.value({})

    # %% State mutation methods %%
    def update_data(self, data_: pd.DataFrame, desc_: pd.DataFrame) -> None:
        """Load data and descriptors atomically.

        Trims data to match desc index and clears derived state
        (surrogates and simulations).

        Args:
            data_: DataFrame with original data
            desc_: DataFrame with calculated descriptors
        """
        # Trim data to match desc index
        data_trimmed = data_[data_.index.isin(desc_.index)]

        # Atomic update
        self.desc.set(desc_)
        self.data.set(data_trimmed)
        self.surr.set({})  # Clear derived state
        self.sim.set({})

    def update_surrogates(self, surr_: dict, sim_: dict) -> None:
        """Update surrogate selection results.

        Args:
            surr_: dict of strategy -> (indices array, LARD score)
            sim_: dict of simulation results for comparison
        """
        self.surr.set(surr_)
        self.sim.set(sim_)

    # %% Computed values %%
    def surrogate_labels(self) -> list:
        """Reactively compute surrogate labels for all data points.

        For each data point, creates a label string indicating which
        surrogate selection strategies selected that point. Used for
        visualization coloring.

        Returns:
            list of label strings, one per data point
        """
        # Initialize empty labels for each point
        labels = {i: [] for i in range(self.desc().shape[0])}

        # Collect strategy names for each point
        for strat, (idx, _) in self.surr().items():
            for i in idx:
                labels[i].append(strat)

        # Convert to sorted comma-separated strings
        return ["&".join(sorted(x)) if x else "none" for x in labels.values()]
