"""Shared data loading for GDP Spurious Regression notebooks."""

import os
import pandas as pd

def load_dataset():
    """Load the GDP dataset and codebook.

    Returns:
        X: Feature DataFrame (all columns except target)
        y: Target Series (gdp_per_capita_usd)
        codebook: Full codebook DataFrame
        role_map: dict mapping column_name -> role
    """
    base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
    df = pd.read_csv(os.path.join(base_dir, 'gdp_spurious_regression_dataset.csv'), index_col=0)
    codebook = pd.read_csv(os.path.join(base_dir, 'codebook.csv'))

    y = df['gdp_per_capita_usd']
    X = df.drop(columns=['gdp_per_capita_usd'])

    role_map = dict(zip(codebook['column_name'], codebook['role']))

    return X, y, codebook, role_map
