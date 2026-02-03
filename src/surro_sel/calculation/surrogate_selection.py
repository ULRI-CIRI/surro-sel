"""Calculator class to perform chemical space surrogate selection.

This class implements multiple surrogate selection strategies as
proposed by Charest et al. (2025): DOI:10.1007/s00216-025-05919-8.

The strategies include:
- RANDOM: Random selection of surrogates
- LOWEST: Selection of surrogates with the lowest leverage
- HIGHEST: Selection of surrogates with the highest leverage
- BALANCED: Alternate selection of surrogates with lowest and highest leverage
- HIERARCHICAL: Hierarchical clustering to select representative surrogates

Surrogate selection outcomes are scored according to the LARD (Leveraged
Averaged Representative Distance) metric as described in the same
publication.
"""

from enum import StrEnum, auto

import numpy as np
from scipy.spatial.distance import cdist
from sklearn.cluster import AgglomerativeClustering
from sklearn.preprocessing import StandardScaler


class SurrogateSelection:
    """Calculator class for chemical space surrogate selection."""

    class Strategy(StrEnum):
        """Enum for implemented surrogate selection strategies."""

        RANDOM = auto()
        LOWEST = auto()
        HIGHEST = auto()
        BALANCED = auto()
        HIERARCHICAL = auto()

    def __init__(self, desc):
        """Constructor for SurrogateSelection calculator class.

        Args:
            desc: non-standardized ionization efficiency descriptor matrix
        """

        # Store a mean-variance standardized array of the input descriptors
        self.X = StandardScaler().fit_transform(desc)
        # Calculate leverages for all data points
        self.h = np.diagonal(self.X.dot(np.linalg.inv(self.X.T.dot(self.X)).dot(self.X.T)))

    def _lowest_n_leverage(self, n):
        return np.argpartition(self.h, n, axis=0)[:n:]

    def _highest_n_leverage(self, n):
        return np.argpartition(self.h, -n, axis=0)[-n::]

    @staticmethod
    def _medoid(x):
        return np.argmin(cdist(x, np.mean(x, axis=0).reshape(1, -1)))

    def score(self, s):
        """Calculate LARD score for a set of surrogates.

        Args:
            s: indices of selected surrogates
        Returns:
            LARD score for selected surrogates
        """

        return np.dot(self.h, np.min(cdist(self.X, self.X[s]), axis=1)) / self.X.shape[0]

    def select(self, n, strategy):
        """Select surrogates based on specified strategy and number.

        Args:
            n: number of surrogates or fraction of dataset to select
            strategy: selection strategy to use
        Returns:
            tuple of selected surrogate indices and corresponding LARD score
        """

        # Calculate "effective" n depending on whether input is < 1
        X_size = self.X.shape[0]
        # Ensure n is not larger than dataset size
        n_eff = min(round(n * X_size if n < 1 else n), X_size)

        # Select surrogates based on the specified strategy
        match strategy:
            case self.Strategy.LOWEST:
                surrogates = self._lowest_n_leverage(n_eff)
            case self.Strategy.HIGHEST:
                surrogates = self._highest_n_leverage(n_eff)
            case self.Strategy.BALANCED:
                n_half = int(n_eff / 2)
                surrogates = np.concatenate(
                    [self._highest_n_leverage(n_half), self._lowest_n_leverage(n_eff - n_half)]
                )
            case self.Strategy.HIERARCHICAL:
                clusters = AgglomerativeClustering(n_clusters=n_eff).fit_predict(self.X)
                cl_idx = [np.where(clusters == cl)[0] for cl in range(n_eff)]
                surrogates = [idx[self._medoid(self.X[idx])] for idx in cl_idx]
            case _:
                # Default to random selection
                surrogates = np.random.choice(X_size, n_eff, replace=False)

        # Return surrogate indices and LARD score
        return surrogates, self.score(surrogates)
