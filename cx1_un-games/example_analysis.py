#!/usr/bin/env python3
"""
Example Analysis: GDP Spurious Regression Dataset

This script demonstrates basic analysis and model comparison
to showcase overfitting and regularization benefits.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso, ElasticNet
from sklearn.ensemble import RandomForestRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score, mean_squared_error

# Suppress warnings for cleaner output
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("GDP SPURIOUS REGRESSION DATASET - EXAMPLE ANALYSIS")
print("=" * 80)

# Load data
print("\n[1] Loading data...")
df = pd.read_csv('gdp_spurious_regression_dataset.csv', index_col=0)
codebook = pd.read_csv('codebook.csv')

print(f"    Dataset: {df.shape[0]} countries × {df.shape[1]} features")

# Separate target and features
y = df['gdp_per_capita_usd']
X = df.drop(columns=['gdp_per_capita_usd'])

print(f"    Target: {y.name}")
print(f"    Features: {X.shape[1]}")

# Feature categories
causal = codebook[codebook['role'] == 'causal']['column_name'].tolist()
bizarre = codebook[codebook['role'] == 'bizarre']['column_name'].tolist()
noise = codebook[codebook['role'] == 'noise']['column_name'].tolist()

print(f"\n    Feature breakdown:")
print(f"      - Causal:  {len(causal)}")
print(f"      - Bizarre: {len(bizarre)}")
print(f"      - Noise:   {len(noise)}")

# Train/test split
print("\n[2] Splitting data (80/20 train/test)...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"    Training set: {X_train.shape[0]} countries")
print(f"    Test set:     {X_test.shape[0]} countries")

# Standardize
print("\n[3] Standardizing features...")
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Model comparison
print("\n[4] Training models...")
print("\n" + "=" * 80)
print("MODEL COMPARISON")
print("=" * 80)

models = {
    'OLS (No Regularization)': LinearRegression(),
    'Ridge (α=1)': Ridge(alpha=1),
    'Ridge (α=10)': Ridge(alpha=10),
    'Ridge (α=100)': Ridge(alpha=100),
    'Lasso (α=1)': Lasso(alpha=1, max_iter=5000),
    'Lasso (α=10)': Lasso(alpha=10, max_iter=5000),
    'Lasso (α=100)': Lasso(alpha=100, max_iter=5000),
    'Elastic Net (α=10)': ElasticNet(alpha=10, max_iter=5000),
    'Random Forest (100 trees)': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
    'Random Forest (500 trees)': RandomForestRegressor(n_estimators=500, max_depth=15, random_state=42, n_jobs=-1),
    'Neural Network (100,50)': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=1000, random_state=42, early_stopping=True, validation_fraction=0.1),
    'Neural Network (200,100,50)': MLPRegressor(hidden_layer_sizes=(200, 100, 50), max_iter=1000, random_state=42, early_stopping=True, validation_fraction=0.1),
}

results = []

for name, model in models.items():
    model.fit(X_train_scaled, y_train)

    # Predictions
    y_train_pred = model.predict(X_train_scaled)
    y_test_pred = model.predict(X_test_scaled)

    # Metrics
    train_r2 = r2_score(y_train, y_train_pred)
    test_r2 = r2_score(y_test, y_test_pred)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_train_pred))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_test_pred))

    # Cross-validation
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='r2')
    cv_mean = cv_scores.mean()
    cv_std = cv_scores.std()

    results.append({
        'Model': name,
        'Train R²': train_r2,
        'Test R²': test_r2,
        'CV R² (mean)': cv_mean,
        'CV R² (std)': cv_std,
        'Overfit Gap': train_r2 - test_r2,
        'Train RMSE': train_rmse,
        'Test RMSE': test_rmse,
    })

    print(f"\n{name}:")
    print(f"  Train R²:        {train_r2:.4f}")
    print(f"  Test R²:         {test_r2:.4f}")
    print(f"  CV R² (5-fold):  {cv_mean:.4f} ± {cv_std:.4f}")
    print(f"  Overfit gap:     {train_r2 - test_r2:.4f}")
    print(f"  Test RMSE:       ${test_rmse:,.2f}")

# Summary table
print("\n" + "=" * 80)
print("RESULTS SUMMARY TABLE")
print("=" * 80)

results_df = pd.DataFrame(results)
print("\n" + results_df.to_string(index=False))

# Feature selection analysis (Lasso)
print("\n" + "=" * 80)
print("FEATURE SELECTION: LASSO (α=10)")
print("=" * 80)

lasso = Lasso(alpha=10, max_iter=5000).fit(X_train_scaled, y_train)

# Count non-zero coefficients
n_selected = np.sum(lasso.coef_ != 0)
print(f"\nSelected {n_selected} out of {len(lasso.coef_)} features ({n_selected/len(lasso.coef_)*100:.1f}%)")

# Top features
coef_df = pd.DataFrame({
    'feature': X.columns,
    'coefficient': lasso.coef_,
    'abs_coef': np.abs(lasso.coef_)
}).sort_values('abs_coef', ascending=False)

# Add role
coef_df['role'] = coef_df['feature'].map(
    dict(zip(codebook['column_name'], codebook['role']))
)

# Non-zero features
nonzero = coef_df[coef_df['abs_coef'] > 0]

print(f"\nTop 20 selected features:")
print(nonzero.head(20)[['feature', 'coefficient', 'role']].to_string(index=False))

# Count by role
print(f"\nSelected features by category:")
for role in ['causal', 'bizarre', 'noise']:
    count = len(nonzero[nonzero['role'] == role])
    total = len(codebook[codebook['role'] == role])
    print(f"  {role.capitalize():<10} {count:3} / {total:3} ({count/total*100:.1f}% selected)")

# Bizarre features that made it through
bizarre_selected = nonzero[nonzero['role'] == 'bizarre']
if len(bizarre_selected) > 0:
    print(f"\n⚠️  BIZARRE FEATURES SELECTED BY LASSO:")
    for _, row in bizarre_selected.iterrows():
        print(f"    - {row['feature']:<40} (coef: {row['coefficient']:+.2f})")
else:
    print(f"\n✓ No bizarre features selected (good!)")

# Key insights
print("\n" + "=" * 80)
print("KEY INSIGHTS")
print("=" * 80)

ols_result = results_df[results_df['Model'] == 'OLS (No Regularization)'].iloc[0]
best_test = results_df.loc[results_df['Test R²'].idxmax()]

print(f"\n1. OVERFITTING IN OLS:")
print(f"   - Training R²: {ols_result['Train R²']:.4f}")
print(f"   - Test R²:     {ols_result['Test R²']:.4f}")
print(f"   - Overfit gap: {ols_result['Overfit Gap']:.4f}")
if ols_result['Overfit Gap'] > 0.1:
    print(f"   ⚠️  OLS shows severe overfitting!")

print(f"\n2. BEST MODEL ON TEST SET:")
print(f"   - Model:   {best_test['Model']}")
print(f"   - Test R²: {best_test['Test R²']:.4f}")
print(f"   - Overfit: {best_test['Overfit Gap']:.4f}")

print(f"\n3. REGULARIZATION BENEFIT:")
improvement = best_test['Test R²'] - ols_result['Test R²']
print(f"   - Test R² improvement over OLS: {improvement:+.4f}")
if improvement > 0:
    print(f"   ✓ Regularization improves generalization!")

print(f"\n4. FEATURE SELECTION:")
print(f"   - Lasso reduced {len(lasso.coef_)} features to {n_selected}")
print(f"   - Reduction: {(1 - n_selected/len(lasso.coef_))*100:.1f}%")

print("\n" + "=" * 80)
print("CONCLUSIONS")
print("=" * 80)

print("""
This dataset demonstrates classic machine learning lessons:

1. **High-dimensional data (p >> n) leads to overfitting**
   - With 355 features and only 254 observations, OLS can fit
     training data nearly perfectly but fails on test data

2. **Regularization prevents overfitting**
   - Ridge/Lasso constrain coefficients
   - Better test set performance despite lower training R²

3. **Lasso performs automatic feature selection**
   - Shrinks many coefficients to exactly zero
   - Keeps only the most predictive features

4. **Spurious correlations exist**
   - Some bizarre features (UFO sightings, McDonald's locations)
     may appear predictive due to correlation with wealth
   - True causal features generally have stronger, more stable effects

5. **Cross-validation is essential**
   - Single train/test split can be misleading
   - CV gives better estimate of generalization

For teaching: Have students plot learning curves, vary alpha values,
compare feature importances, and discuss which features make economic sense!
""")

print("=" * 80)
print("✓ Analysis complete! Try modifying this script to explore further.")
print("=" * 80)
