---
title: GDP Spurious Regression — Interactive ML Workshop
emoji: 📊
colorFrom: blue
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# GDP Spurious Regression — Interactive ML Workshop

An interactive teaching tool that demonstrates overfitting, regularization, and spurious correlations using a real-world-inspired dataset of 254 countries and 493 features.

## Modules

1. **Explore the Data** — Discover which features correlate with GDP (and why correlation is not causation)
2. **Overfitting** — Watch OLS memorize training data perfectly yet fail on test data
3. **Regularization** — See how Ridge and Lasso constrain coefficients to improve generalization
4. **Spurious Features** — Compare Random Forest vs Lasso: who gets fooled by fake predictors?
5. **Cross-Validation** — Confirm results are reliable across multiple splits

## Dataset

- 254 countries, 493 features + 1 target (GDP per capita)
- 22 causal features (real economic/development indicators)
- 333 spurious features (flag colors, numerology scores, Scrabble values, synthetic noise)
- 138 incidental features (geographic, demographic)

Built for the Business Methods and AI course (BMAI), ETH Zurich.
