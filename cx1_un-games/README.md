# GDP Spurious Regression Dataset

## Notebooks

Work through the five interactive modules in Google Colab — no local setup needed:

| Module | Topic | Open in Colab |
|--------|-------|---------------|
| 01 | Explore the Data | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eth-bmai-fs26/coding-exercises/blob/week1/cx1_un-games/notebooks/01_explore_the_data.ipynb) |
| 02 | Overfitting | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eth-bmai-fs26/coding-exercises/blob/week1/cx1_un-games/notebooks/02_overfitting.ipynb) |
| 03 | Regularization | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eth-bmai-fs26/coding-exercises/blob/week1/cx1_un-games/notebooks/03_regularization.ipynb) |
| 04 | Spurious Features & Random Forest | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eth-bmai-fs26/coding-exercises/blob/week1/cx1_un-games/notebooks/04_spurious_features.ipynb) |
| 05 | Cross-Validation | [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/eth-bmai-fs26/coding-exercises/blob/week1/cx1_un-games/notebooks/05_cross_validation.ipynb) |

> **Getting started:** click any badge above, then run the first cell — it downloads the data and sets up all dependencies automatically.

---

## Overview

This dataset is designed for teaching machine learning concepts related to **spurious regression**, **overfitting**, and **regularization techniques**. It contains GDP per capita as the target variable along with a mix of genuinely predictive features, absurd correlates, and pure noise.

## Dataset Specifications

- **Countries**: 254
- **Total Features**: 273
- **Target Variable**: `gdp_per_capita_usd` (GDP per capita, current US$, year 2020)
- **Reference Year**: 2020 (with 2019 fallback for some indicators)

## Feature Categories

### 1. Causal/Meaningful Covariates (~22 features)
Features with genuine economic theory behind their relationship to GDP:
- **Human Capital**: Life expectancy, education enrollment, literacy rates
- **Institutions**: Governance indicators (rule of law, corruption control, regulatory quality)
- **Investment**: Capital formation, FDI, savings
- **Trade**: Exports, trade openness
- **Infrastructure**: Internet penetration, mobile subscriptions, electricity consumption
- **Demographics**: Urban population, fertility rate, infant mortality

### 2. Bizarre Covariates (~27 features)
Features with absurd or spurious correlations to GDP:

**Competitions & Awards:**
- Eurovision Song Contest wins
- FIFA World Cup wins (men's and women's)
- Olympic medals (total and per capita)
- Nobel Prize winners (total and per capita)
- Miss Universe wins
- Michelin stars

**Retail & Consumer Culture:**
- IKEA stores
- McDonald's restaurants
- Starbucks locations

**Lifestyle & Consumption:**
- Beer consumption per capita
- Wine consumption per capita
- Coffee consumption per capita

**Infrastructure & Entertainment:**
- Casinos
- Airports
- Skyscrapers over 150m
- Theme parks
- Golf courses
- Cryptocurrency ATMs

**Cultural & Natural:**
- UNESCO World Heritage Sites
- Active volcanoes

**Geographic Oddities:**
- Number of time zones
- Number of land border countries

**Country Name Features:**
- Letters, vowels, consonants in country name
- Number of words in country name
- Whether country name starts with a vowel

### 3. Noise Covariates (~320 features)
Features unlikely to have genuine predictive power:

#### Real-world noise indicators from World Bank WDI:
- Energy: Coal/gas/nuclear electricity generation, energy imports, consumption
- Infrastructure: Air transport, rail lines, road networks, ports
- Finance: Bank ratios, interest rates, reserves
- Labor: Employment by sector, vulnerable employment, self-employment
- Demographics: Age dependency ratios, birth/death rates, urban growth
- Agriculture: Production indices, yields, land use, precipitation
- Environment: Greenhouse gas emissions, threatened species, fisheries
- Trade: Sector-specific imports/exports (fuels, food, manufactures, high-tech)
- Technology: R&D expenditure, patents, journal articles, broadband
- Health: Immunization rates, water/sanitation access, disease-specific mortality
- Poverty: GINI index, poverty headcount, income distribution
- Government: Revenue, expenses, deficits
- Tourism: Arrivals, receipts, departures
- Education: Gender-specific literacy, expenditure per student

#### Transformed features:
- Log, square, and cube root transformations of existing features
- Polynomial interaction terms (products of feature pairs)

#### Pure synthetic noise:
- Random Gaussian, uniform, and exponential noise features

## Data Sources

1. **World Bank World Development Indicators (WDI)**: Primary source for economic, social, and development indicators
2. **World Bank World Governance Indicators (WGI)**: Governance quality metrics
3. **Nobel Prize API**: Historical laureate data
4. **Compiled Data Sources**: Olympic medals, UNESCO sites, retail locations (Wikipedia, official sources)
5. **Synthetic**: Random noise features for padding

## Data Processing

### Missing Data Handling
1. Countries with >50% missing values across all features were dropped
2. Features with >30% missing values across countries were dropped
3. Remaining missing values were imputed using column medians

### Data Quality
- All features are numeric
- No missing values in the final dataset
- ISO 3166-1 alpha-3 country codes used as index
- Target variable (GDP per capita) ranges from $255.83 to $176,891.89

## Files

- `gdp_spurious_regression_dataset.csv`: Main dataset (254 rows × 356 columns)
- `codebook.csv`: Feature documentation with columns:
  - `column_name`: Feature name
  - `description`: Human-readable description
  - `source`: Data source
  - `role`: One of "target", "causal", "bizarre", "noise"

## Intended Use Cases

This dataset is perfect for demonstrating:

1. **Overfitting**: With p >> n (356 features, 254 observations), models can easily overfit
2. **Feature Selection**: Identifying truly predictive features among noise
3. **Regularization**: Comparing Ridge, Lasso, and Elastic Net
4. **Cross-Validation**: Proper model evaluation techniques
5. **Spurious Correlations**: How absurd features (e.g., Miss Universe wins) can appear predictive
6. **Dimensionality Reduction**: PCA, feature importance, etc.
7. **Model Interpretability**: Understanding what models actually learn

## Example ML Workflow

```python
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.preprocessing import StandardScaler

# Load data
df = pd.read_csv('gdp_spurious_regression_dataset.csv', index_col=0)
codebook = pd.read_csv('codebook.csv')

# Separate target and features
y = df['gdp_per_capita_usd']
X = df.drop(columns=['gdp_per_capita_usd'])

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Standardize
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Compare models
models = {
    'OLS': LinearRegression(),
    'Ridge': Ridge(alpha=10),
    'Lasso': Lasso(alpha=10),
}

for name, model in models.items():
    model.fit(X_train_scaled, y_train)
    train_score = model.score(X_train_scaled, y_train)
    test_score = model.score(X_test_scaled, y_test)
    print(f"{name}:")
    print(f"  Train R²: {train_score:.4f}")
    print(f"  Test R²:  {test_score:.4f}")
    print()

# Feature importance (for Lasso)
lasso = Lasso(alpha=10).fit(X_train_scaled, y_train)
coef_df = pd.DataFrame({
    'feature': X.columns,
    'coefficient': lasso.coef_,
    'abs_coef': np.abs(lasso.coef_)
}).sort_values('abs_coef', ascending=False)

print("Top 10 features by Lasso coefficient:")
print(coef_df.head(10))

# See which bizarre features made it through
bizarre_features = codebook[codebook['role'] == 'bizarre']['column_name'].values
bizarre_in_top = coef_df[coef_df['feature'].isin(bizarre_features)].head(5)
print("\nTop bizarre features:")
print(bizarre_in_top)
```

## Expected Learning Outcomes

Students working with this dataset should learn:

1. **High R² on training data doesn't mean good model**: OLS will likely achieve R² > 0.95 on training but fail on test data
2. **Regularization prevents overfitting**: Ridge/Lasso will have lower training R² but better test performance
3. **Feature selection matters**: Lasso automatically zeros out noise features
4. **Bizarre correlations exist**: Some absurd features (e.g., McDonald's locations) may appear predictive due to correlation with wealth
5. **Cross-validation is essential**: Single train/test splits can be misleading

## Limitations

1. **FAOSTAT data unavailable**: Originally planned to include ~95 food commodities, but the FAO API was unavailable during dataset creation
2. **2020 COVID effects**: Some indicators may be affected by the pandemic
3. **Missing data bias**: Countries with poor data infrastructure may be underrepresented
4. **Temporal snapshot**: Cross-sectional data from a single year (2020/2019)

## Citation

If using this dataset, please cite:
- World Bank World Development Indicators: https://data.worldbank.org/
- World Bank Worldwide Governance Indicators: https://info.worldbank.org/governance/wgi/
- Nobel Prize API: https://www.nobelprize.org/about/developer-zone-2/

## License

This dataset compilation is provided for educational purposes. Individual data sources retain their original licenses:
- World Bank data: CC BY 4.0
- Nobel Prize data: CC0 1.0
- Synthetic/compiled data: CC BY 4.0

## Version

- **Version**: 1.0
- **Created**: February 2026
- **Last Updated**: February 2026

## Contact

For questions or issues with this dataset, please refer to the source repositories and APIs listed above.

---

**Happy learning! May your models overfit spectacularly before you fix them with regularization! 🎓📊**
