#!/usr/bin/env python3
"""
Remove Transformations and Interactions of Causal Features

This script removes all polynomial transformations (log, square, cube root)
and interaction terms that were created from causal features, as they allow
models to "cheat" by having multiple views of the same causal information.
"""

import pandas as pd
import re

print("=" * 80)
print("CLEANING UP TRANSFORMATIONS OF CAUSAL FEATURES")
print("=" * 80)

# Load dataset and codebook
df = pd.read_csv('gdp_spurious_regression_dataset.csv', index_col=0)
codebook_df = pd.read_csv('codebook.csv')

print(f"\nStarting: {df.shape[0]} countries × {df.shape[1]} features")

# Get all causal feature names
causal_features = codebook_df[codebook_df['role'] == 'causal']['column_name'].tolist()
print(f"Causal features: {len(causal_features)}")

# Identify columns to remove
cols_to_remove = []

# Pattern 1: Transformations (log, squared, cbrt) of any feature
transformation_patterns = ['_log', '_squared', '_cbrt']
for col in df.columns:
    if any(pattern in col for pattern in transformation_patterns):
        cols_to_remove.append(col)

# Pattern 2: Interactions (feature_x_feature)
for col in df.columns:
    if '_x_' in col:
        cols_to_remove.append(col)

# Remove duplicates
cols_to_remove = list(set(cols_to_remove))

print(f"\n Identified {len(cols_to_remove)} transformation/interaction features to remove:")

# Categorize what we're removing
transformations = [c for c in cols_to_remove if any(p in c for p in transformation_patterns) and '_x_' not in c]
interactions = [c for c in cols_to_remove if '_x_' in c]

print(f"  - {len(transformations)} transformations (log, squared, cbrt)")
print(f"  - {len(interactions)} interaction terms (feature × feature)")

# Show examples
if transformations:
    print(f"\n  Example transformations:")
    for col in transformations[:5]:
        print(f"    • {col}")

if interactions:
    print(f"\n  Example interactions:")
    for col in interactions[:5]:
        print(f"    • {col}")

# Remove from dataframe
df_clean = df.drop(columns=cols_to_remove)

# Remove from codebook
codebook_clean = codebook_df[~codebook_df['column_name'].isin(cols_to_remove)]

print(f"\n" + "=" * 80)
print("RESULTS")
print("=" * 80)

print(f"\nDataset shape:")
print(f"  Before: {df.shape[0]} countries × {df.shape[1]} features")
print(f"  After:  {df_clean.shape[0]} countries × {df_clean.shape[1]} features")
print(f"  Removed: {df.shape[1] - df_clean.shape[1]} features")

# Update role counts
role_counts_before = codebook_df['role'].value_counts()
role_counts_after = codebook_clean['role'].value_counts()

print(f"\nFeature breakdown by role:")
print(f"  {'Role':<12} {'Before':>8} {'After':>8} {'Change':>8}")
print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*8}")
for role in ['target', 'causal', 'bizarre', 'noise']:
    before = role_counts_before.get(role, 0)
    after = role_counts_after.get(role, 0)
    change = after - before
    print(f"  {role.capitalize():<12} {before:>8} {after:>8} {change:>+8}")

# Check noise composition
noise_features = codebook_clean[codebook_clean['role'] == 'noise']
synthetic = sum(1 for f in noise_features['column_name'] if 'synthetic' in f)
real_noise = len(noise_features) - synthetic

print(f"\nNoise composition (after cleanup):")
print(f"  Real-world noise:  {real_noise:>3} features ({100*real_noise/len(noise_features):>5.1f}%)")
print(f"  Synthetic noise:   {synthetic:>3} features ({100*synthetic/len(noise_features):>5.1f}%)")

# Save
df_clean.to_csv('gdp_spurious_regression_dataset.csv', index=True)
codebook_clean.to_csv('codebook.csv', index=False)

print(f"\n" + "=" * 80)
print("✓ CLEANUP COMPLETE!")
print("=" * 80)

print("\nDataset is now cleaner:")
print("  ✓ No polynomial transformations of features")
print("  ✓ No interaction terms")
print("  ✓ Each feature appears only once")
print("  ✓ Causal features are in their original form")
print("  ✓ Better for teaching feature selection!")

print(f"\nMissing values: {df_clean.isnull().sum().sum()}")
print("\nFiles updated:")
print("  - gdp_spurious_regression_dataset.csv")
print("  - codebook.csv")
