"""
Proliferate bizarre features in the GDP spurious regression dataset.

Generates 260 new bizarre features using sin, cos, interaction, and ratio
transformations of existing bizarre features, then saves them back to the
dataset and codebook.
"""

import numpy as np
import pandas as pd
import os

# ── Configuration ──────────────────────────────────────────────────────────
SEED = 42
N_SIN = 50
N_COS = 50
N_INTERACTIONS = 80
N_RATIOS = 80
N_TOTAL = N_SIN + N_COS + N_INTERACTIONS + N_RATIOS  # 260

FREQUENCIES = [1, 2, 3, 5, 7]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(SCRIPT_DIR, "gdp_spurious_regression_dataset.csv")
CODEBOOK_PATH = os.path.join(SCRIPT_DIR, "codebook.csv")

# ── Reproducibility ───────────────────────────────────────────────────────
rng = np.random.RandomState(SEED)

# ── Load data ─────────────────────────────────────────────────────────────
df = pd.read_csv(DATA_PATH, index_col=0)
codebook = pd.read_csv(CODEBOOK_PATH)

# ── Identify existing bizarre features ────────────────────────────────────
bizarre_cols = codebook.loc[codebook["role"] == "bizarre", "column_name"].tolist()
# Keep only those actually present in the dataframe
bizarre_cols = [c for c in bizarre_cols if c in df.columns]
print(f"Found {len(bizarre_cols)} existing bizarre features.")

existing_columns = set(df.columns)

# ── Name generation infrastructure ────────────────────────────────────────
PREFIXES = [
    "cultural", "social", "economic", "demographic", "institutional",
    "developmental", "structural", "composite", "adjusted", "normalized",
    "comparative", "relative", "aggregate", "weighted", "derived",
    "integrated", "holistic", "longitudinal", "transversal", "systemic",
    "foundational", "progressive", "empirical", "analytical", "regional",
    "national", "sectoral", "multifactorial", "observed", "estimated",
]

SUFFIXES = [
    "index", "metric", "indicator", "score", "factor",
    "quotient", "coefficient", "measure", "rate", "parameter",
    "benchmark", "estimator", "proxy", "signal", "value",
]

MIDWORDS = [
    "development", "governance", "welfare", "stability", "resilience",
    "prosperity", "equity", "capacity", "infrastructure", "progress",
    "sustainability", "growth", "transformation", "cohesion", "inclusion",
    "mobility", "productivity", "efficiency", "opportunity", "heritage",
    "engagement", "participation", "vitality", "convergence", "adaptation",
]

DESCRIPTIONS = [
    "Derived socioeconomic indicator",
    "Composite development metric",
    "Aggregated institutional measure",
    "Normalized welfare benchmark",
    "Structural capacity estimator",
    "Integrated progress parameter",
    "Multifactorial development index",
    "Weighted governance proxy",
    "Longitudinal stability metric",
    "Empirical resilience score",
    "Regional prosperity indicator",
    "Systemic cohesion factor",
    "Analytical growth coefficient",
    "Comparative equity measure",
    "Observed participation rate",
]


def generate_unique_name(used_names, counter):
    """Generate a unique plausible-sounding feature name."""
    while True:
        prefix = rng.choice(PREFIXES)
        midword = rng.choice(MIDWORDS)
        suffix = rng.choice(SUFFIXES)
        name = f"{prefix}_{midword}_{suffix}_{counter}"
        if name not in used_names and name not in existing_columns:
            used_names.add(name)
            return name
        counter += 1


def normalize_to_range(x, lo=0, hi=2 * np.pi):
    """Normalize a series to [lo, hi], handling constant columns."""
    xmin = x.min()
    xmax = x.max()
    if xmax == xmin:
        return pd.Series(np.full(len(x), (lo + hi) / 2), index=x.index)
    return lo + (x - xmin) / (xmax - xmin) * (hi - lo)


# ── Generate features ─────────────────────────────────────────────────────
used_names = set()
new_features = {}
new_codebook_rows = []
counter = 1


def add_feature(series, name):
    """Register a new feature column and its codebook entry."""
    global counter
    desc = rng.choice(DESCRIPTIONS)
    new_features[name] = series.values
    new_codebook_rows.append({
        "column_name": name,
        "description": desc,
        "source": "Derived (computed)",
        "role": "bizarre",
    })
    counter += 1


# ── 1) Sin features (~50) ─────────────────────────────────────────────────
print("Generating sin features...")
for i in range(N_SIN):
    col = rng.choice(bizarre_cols)
    k = rng.choice(FREQUENCIES)
    x_norm = normalize_to_range(df[col].astype(float))
    values = np.sin(k * x_norm)
    name = generate_unique_name(used_names, counter)
    add_feature(pd.Series(values, index=df.index), name)

# ── 2) Cos features (~50) ─────────────────────────────────────────────────
print("Generating cos features...")
for i in range(N_COS):
    col = rng.choice(bizarre_cols)
    k = rng.choice(FREQUENCIES)
    x_norm = normalize_to_range(df[col].astype(float))
    values = np.cos(k * x_norm)
    name = generate_unique_name(used_names, counter)
    add_feature(pd.Series(values, index=df.index), name)

# ── 3) Interaction features (~80) ─────────────────────────────────────────
print("Generating interaction features...")
for i in range(N_INTERACTIONS):
    col_i, col_j = rng.choice(bizarre_cols, size=2, replace=False)
    values = df[col_i].astype(float) * df[col_j].astype(float)
    name = generate_unique_name(used_names, counter)
    add_feature(values, name)

# ── 4) Ratio features (~80) ──────────────────────────────────────────────
print("Generating ratio features...")
for i in range(N_RATIOS):
    col_i, col_j = rng.choice(bizarre_cols, size=2, replace=False)
    x_j = df[col_j].astype(float)
    # Compute epsilon: 1st percentile of nonzero absolute values, or 1.0
    nonzero_vals = np.abs(x_j[x_j != 0].values)
    if len(nonzero_vals) > 0:
        eps = min(np.percentile(nonzero_vals, 1), 1.0)
    else:
        eps = 1.0
    values = df[col_i].astype(float) / (x_j + eps)
    name = generate_unique_name(used_names, counter)
    add_feature(values, name)

# ── Add new features to the dataframe ─────────────────────────────────────
print(f"\nAdding {len(new_features)} new features to the dataset...")
new_df = pd.DataFrame(new_features, index=df.index)
df = pd.concat([df, new_df], axis=1)

# ── Save updated dataset ─────────────────────────────────────────────────
df.to_csv(DATA_PATH)
print(f"Saved dataset to {DATA_PATH}")

# ── Update and save codebook ─────────────────────────────────────────────
new_codebook_df = pd.DataFrame(new_codebook_rows)
codebook = pd.concat([codebook, new_codebook_df], ignore_index=True)
codebook.to_csv(CODEBOOK_PATH, index=False)
print(f"Saved codebook to {CODEBOOK_PATH}")

# ── Summary ───────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print(f"Features created:")
print(f"  Sin:          {N_SIN}")
print(f"  Cos:          {N_COS}")
print(f"  Interaction:  {N_INTERACTIONS}")
print(f"  Ratio:        {N_RATIOS}")
print(f"  Total:        {N_TOTAL}")

print(f"\nNew dataset shape: {df.shape}")

print(f"\nCodebook breakdown by role:")
for role, count in codebook["role"].value_counts().items():
    print(f"  {role}: {count}")

# ── Spot check: correlation of 5 random new features with GDP ─────────────
print("\nSpot check: Pearson correlation of 5 random new features with gdp_per_capita_usd:")
new_feature_names = list(new_features.keys())
sample_cols = rng.choice(new_feature_names, size=5, replace=False)
for col in sample_cols:
    corr = df[col].corr(df["gdp_per_capita_usd"])
    print(f"  {col}: {corr:.4f}")

print("\nDone.")
