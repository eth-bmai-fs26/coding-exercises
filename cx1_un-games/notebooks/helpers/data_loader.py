"""Shared data loading for GDP Spurious Regression notebooks."""

import os
import pandas as pd


def _find_file(filename):
    # 1. Check current working directory (works in Colab after download)
    cwd_path = os.path.join(os.getcwd(), filename)
    if os.path.exists(cwd_path):
        return cwd_path
    # 2. Fall back to relative path from __file__ (local dev layout)
    base_dir = os.path.join(os.path.dirname(__file__), '..', '..')
    return os.path.join(base_dir, filename)


def load_dataset():
    """Load the GDP dataset and codebook.

    Returns:
        X: Feature DataFrame (all columns except target)
        y: Target Series (gdp_per_capita_usd)
        codebook: Full codebook DataFrame
        role_map: dict mapping column_name -> role
    """
    df = pd.read_csv(_find_file('gdp_spurious_regression_dataset.csv'), index_col=0)
    codebook = pd.read_csv(_find_file('codebook.csv'))

    y = df['gdp_per_capita_usd']
    X = df.drop(columns=['gdp_per_capita_usd'])

    role_map = dict(zip(codebook['column_name'], codebook['role']))

    return X, y, codebook, role_map
