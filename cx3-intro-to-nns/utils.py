# ============================================================
# utils.py — Helper functions for the Neural Network notebooks
#
# This file contains all the "boilerplate" code so the
# notebooks can focus on the parts that matter most.
#
# You can open this file any time to see exactly what each
# helper function does under the hood.
# ============================================================

# --- Deep learning ---
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

# --- Data handling ---
import numpy as np
import pandas as pd
import kagglehub
import os

# --- Machine learning utilities ---
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

# --- Visualization ---
import matplotlib.pyplot as plt
import seaborn as sns

# Apply a clean visual style for all plots
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (10, 6)


# ============================================================
# 1. DATA LOADING
# ============================================================

def load_dataset():
    """
    Download the house price dataset from Kaggle, load it into a
    table, and remove houses with extreme outlier prices.

    Returns a pandas DataFrame with one row per house.
    """
    print("Downloading dataset from Kaggle...")
    dataset_path = kagglehub.dataset_download(
        'muhamedumarjamil/house-price-prediction-dataset'
    )

    csv_file = os.path.join(dataset_path, 'house_prices_dataset.csv')
    df = pd.read_csv(csv_file)

    print(f"Dataset loaded: {len(df)} houses, {len(df.columns)} columns")

    # Remove extreme outliers (prices more than 3 std from the mean in log space)
    log_prices = np.log(df['price'])
    outlier_mask = np.abs(log_prices - log_prices.mean()) <= 3 * log_prices.std()
    df = df[outlier_mask].copy()

    print(f"After removing extreme outliers: {len(df)} houses remaining")
    print("Dataset ready!")
    return df


# ============================================================
# 2. DATA VISUALIZATION
# ============================================================

def plot_dataset(df):
    """
    Show 4 charts to explore the house price dataset:
      1. Distribution of house prices
      2. Which features are most correlated with price
      3. House size vs price
      4. House age vs price
    """
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. Distribution of house prices
    axes[0, 0].hist(df['price'], bins=50, color='steelblue',
                    edgecolor='white', alpha=0.7)
    axes[0, 0].set_xlabel('House Price ($)')
    axes[0, 0].set_ylabel('Frequency')
    axes[0, 0].set_title('Distribution of House Prices')
    axes[0, 0].axvline(df['price'].mean(), color='red', linestyle='--',
                       label=f'Mean: ${df["price"].mean():,.0f}')
    axes[0, 0].legend()

    # 2. Feature correlations with price
    feature_cols = [c for c in df.columns if c != 'price']
    correlations = [df[c].corr(df['price']) for c in feature_cols]
    colors = ['green' if c > 0 else 'red' for c in correlations]
    axes[0, 1].barh(feature_cols, correlations, color=colors, alpha=0.7)
    axes[0, 1].set_xlabel('Correlation with Price')
    axes[0, 1].set_title('Feature Correlation with House Price')
    axes[0, 1].axvline(0, color='black', linewidth=0.5)

    # 3. House size vs price
    axes[1, 0].scatter(df['square_feet'], df['price'], alpha=0.3, s=5,
                       c='steelblue')
    axes[1, 0].set_xlabel('Square Feet')
    axes[1, 0].set_ylabel('Price ($)')
    axes[1, 0].set_title('House Size vs Price')

    # 4. House age vs price
    axes[1, 1].scatter(df['age'], df['price'], alpha=0.3, s=5, c='green')
    axes[1, 1].set_xlabel('Age (years)')
    axes[1, 1].set_ylabel('Price ($)')
    axes[1, 1].set_title('House Age vs Price')

    plt.tight_layout()
    plt.show()


# ============================================================
# 3. DATA PREPARATION — BASE NOTEBOOK
# ============================================================

def prepare_data(df):
    """
    Get the dataset ready for training (base notebook version).

    Steps done inside this function:
      1. Separate features (inputs) from the target (price)
      2. Split into train / validation / test sets (80% / 10% / 10%)
      3. Standardize all values so the model trains efficiently
      4. Convert everything to PyTorch tensors

    Returns (in order):
      train_features_t, val_features_t, test_features_t   — input tensors
      train_prices_t, val_prices_t, test_prices_t          — scaled price tensors
      test_prices_original                                  — real dollar prices for the test set
      price_scaler                                          — needed to convert predictions back to $
    """
    # Step 1: Separate features and target
    feature_columns = [c for c in df.columns if c != 'price']
    features = df[feature_columns].values          # shape: (N, num_features)
    prices   = df['price'].values.reshape(-1, 1)   # shape: (N, 1)

    # Step 2: Split 80% train / 10% validation / 10% test
    train_feat, temp_feat, train_price, temp_price = train_test_split(
        features, prices, test_size=0.2, random_state=42
    )
    val_feat, test_feat, val_price, test_price = train_test_split(
        temp_feat, temp_price, test_size=0.5, random_state=42
    )

    # Step 3: Scale features (mean=0, std=1) — fit only on training data
    feat_scaler = StandardScaler()
    train_feat = feat_scaler.fit_transform(train_feat)
    val_feat   = feat_scaler.transform(val_feat)
    test_feat  = feat_scaler.transform(test_feat)

    # Scale prices too (needed because we predict raw dollars)
    price_scaler = StandardScaler()
    train_price_scaled = price_scaler.fit_transform(train_price)
    val_price_scaled   = price_scaler.transform(val_price)
    test_price_scaled  = price_scaler.transform(test_price)

    # Step 4: Convert to PyTorch tensors
    train_features_t = torch.tensor(train_feat,          dtype=torch.float32)
    val_features_t   = torch.tensor(val_feat,            dtype=torch.float32)
    test_features_t  = torch.tensor(test_feat,           dtype=torch.float32)
    train_prices_t   = torch.tensor(train_price_scaled,  dtype=torch.float32)
    val_prices_t     = torch.tensor(val_price_scaled,    dtype=torch.float32)
    test_prices_t    = torch.tensor(test_price_scaled,   dtype=torch.float32)

    print(f"Training samples:   {len(train_prices_t)}")
    print(f"Validation samples: {len(val_prices_t)}")
    print(f"Test samples:       {len(test_prices_t)}")
    print(f"Number of features: {train_features_t.shape[1]}")

    return (train_features_t, val_features_t, test_features_t,
            train_prices_t, val_prices_t, test_prices_t,
            test_price, price_scaler)


# ============================================================
# 4. DATA PREPARATION — TRICKS NOTEBOOK
# ============================================================

def split_and_scale_data_tricks(features, log_prices, original_prices):
    """
    Split data into train/val/test sets and scale the features.
    Used in the 'tricks' notebook where the target is log-transformed.

    Note: we only scale the features — log prices are already in a
    good numerical range and don't need scaling.

    Returns (in order):
      train_features, val_features, test_features   — scaled numpy arrays
      train_log_prices, val_log_prices, test_log_prices  — log price arrays
      val_orig_prices, test_orig_prices              — original dollar prices
    """
    # Split 80% train / 10% validation / 10% test
    (train_feat, temp_feat,
     train_log, temp_log,
     train_orig, temp_orig) = train_test_split(
        features, log_prices, original_prices,
        test_size=0.2, random_state=42
    )
    (val_feat, test_feat,
     val_log, test_log,
     val_orig, test_orig) = train_test_split(
        temp_feat, temp_log, temp_orig,
        test_size=0.5, random_state=42
    )

    # Scale features only — fit only on training data to avoid data leakage
    feat_scaler = StandardScaler()
    train_feat = feat_scaler.fit_transform(train_feat)
    val_feat   = feat_scaler.transform(val_feat)
    test_feat  = feat_scaler.transform(test_feat)

    print(f"Training samples:   {len(train_log)}")
    print(f"Validation samples: {len(val_log)}")
    print(f"Test samples:       {len(test_log)}")

    return (train_feat, val_feat, test_feat,
            train_log, val_log, test_log,
            val_orig, test_orig)


def convert_to_tensors(train_feat, val_feat, test_feat,
                       train_prices, val_prices, test_prices):
    """
    Convert six NumPy arrays to PyTorch tensors so they can be
    fed into the neural network.

    Returns (in order):
      train_features_t, val_features_t, test_features_t
      train_prices_t,   val_prices_t,   test_prices_t
    """
    return (
        torch.tensor(train_feat,   dtype=torch.float32),
        torch.tensor(val_feat,     dtype=torch.float32),
        torch.tensor(test_feat,    dtype=torch.float32),
        torch.tensor(train_prices, dtype=torch.float32),
        torch.tensor(val_prices,   dtype=torch.float32),
        torch.tensor(test_prices,  dtype=torch.float32),
    )


# ============================================================
# 5. TRAINING HELPERS
# ============================================================

def run_epoch(model, optimizer, loss_fn, train_X, train_y, val_X, val_y):
    """
    Run one full training epoch on the entire training set,
    then evaluate on the validation set.

    Used in the base notebook (full-batch training).

    Returns:
        train_loss (float): MSE loss on the training set
        val_loss   (float): MSE loss on the validation set
    """
    # Training phase
    model.train()
    predictions = model(train_X)
    train_loss = loss_fn(predictions, train_y)

    optimizer.zero_grad()
    train_loss.backward()
    optimizer.step()

    # Validation phase
    model.eval()
    with torch.no_grad():
        val_predictions = model(val_X)
        val_loss = loss_fn(val_predictions, val_y)

    return train_loss.item(), val_loss.item()


def run_epoch_minibatch(model, optimizer, loss_fn, train_loader, val_X, val_y):
    """
    Run one full training epoch using mini-batches from a DataLoader,
    then evaluate on the full validation set.

    Used in the tricks notebook (mini-batch training).

    Returns:
        train_loss (float): average MSE loss across all training samples
        val_loss   (float): MSE loss on the validation set
    """
    # Training phase (mini-batch)
    model.train()
    epoch_train_loss = 0.0

    for batch_X, batch_y in train_loader:
        predictions = model(batch_X)
        batch_loss = loss_fn(predictions, batch_y)

        optimizer.zero_grad()
        batch_loss.backward()
        optimizer.step()

        epoch_train_loss += batch_loss.item() * len(batch_X)

    epoch_train_loss /= len(train_loader.dataset)

    # Validation phase (full set)
    model.eval()
    with torch.no_grad():
        val_predictions = model(val_X)
        val_loss = loss_fn(val_predictions, val_y)

    return epoch_train_loss, val_loss.item()


# ============================================================
# 6. TRAINING VISUALIZATION
# ============================================================

def plot_training_history(train_losses, val_losses):
    """
    Plot how the training and validation loss changed over time.

    Left panel:  full history on a log scale (shows the big picture)
    Right panel: zoomed into the last 200 epochs (shows fine details)
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Left: full loss curves on log scale
    axes[0].plot(train_losses, label='Training Loss', alpha=0.8)
    axes[0].plot(val_losses,   label='Validation Loss', alpha=0.8)
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('MSE Loss (log scale)')
    axes[0].set_title('Training & Validation Loss Over Time')
    axes[0].legend()
    axes[0].set_yscale('log')

    # Right: zoomed into the last portion
    zoom_epochs = min(200, len(train_losses))
    axes[1].plot(range(len(train_losses) - zoom_epochs, len(train_losses)),
                 train_losses[-zoom_epochs:], label='Training Loss', alpha=0.8)
    axes[1].plot(range(len(val_losses) - zoom_epochs, len(val_losses)),
                 val_losses[-zoom_epochs:], label='Validation Loss', alpha=0.8)
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('MSE Loss')
    axes[1].set_title(f'Loss Convergence (Last {zoom_epochs} Epochs)')
    axes[1].legend()

    plt.tight_layout()
    plt.show()

    print(f"Final Training Loss:   {train_losses[-1]:.4f}")
    print(f"Final Validation Loss: {val_losses[-1]:.4f}")


# ============================================================
# 7. GETTING PREDICTIONS
# ============================================================

def get_predictions(model, test_features_t, price_scaler):
    """
    Run the model on the test set and convert the scaled predictions
    back into real dollar values.

    Used in the base notebook (where prices were scaled with StandardScaler).
    """
    model.eval()
    with torch.no_grad():
        test_pred_scaled = model(test_features_t).numpy()
    return price_scaler.inverse_transform(test_pred_scaled)


def get_predictions_log(model, test_features_t):
    """
    Run the model on the test set and convert log-price predictions
    back into real dollar values using exp().

    Used in the tricks notebook (where the target was log-transformed).
    """
    model.eval()
    with torch.no_grad():
        test_pred_log = model(test_features_t).numpy()
    return np.exp(test_pred_log)


# ============================================================
# 8. EVALUATION METRICS
# ============================================================

def print_performance_metrics(actual_prices, predicted_prices, show_r2=False):
    """
    Print how well the model performed on the test set.

    Shows:
      - MAE  (Mean Absolute Error): average error in dollars
      - RMSE (Root Mean Squared Error): penalises large errors more
      - MAPE (Mean Absolute Percentage Error): error as a % of the real price
      - R²   (Coefficient of Determination): optional, pass show_r2=True

    Also breaks down performance by price range (quartiles).
    """
    actual = actual_prices.flatten()
    pred   = predicted_prices.flatten()

    mae  = np.mean(np.abs(pred - actual))
    rmse = np.sqrt(np.mean((pred - actual) ** 2))
    mape = np.mean(np.abs((pred - actual) / actual)) * 100

    print("=" * 55)
    print("           OVERALL TEST SET PERFORMANCE")
    print("=" * 55)
    print()
    print(f"   MAE  (Mean Absolute Error):      ${mae:,.2f}")
    print(f"   RMSE (Root Mean Squared Error):  ${rmse:,.2f}")
    print(f"   MAPE (Mean Absolute % Error):    {mape:.2f}%")

    if show_r2:
        ss_res   = np.sum((actual - pred) ** 2)
        ss_tot   = np.sum((actual - np.mean(actual)) ** 2)
        r2_score = 1 - (ss_res / ss_tot)
        print(f"   R²   (Coefficient of Determination): {r2_score:.4f}")

    print()
    print("=" * 55)

    # Performance by price range
    quartiles = np.quantile(actual, [0, 0.25, 0.5, 0.75, 1.0])

    print()
    print("        PERFORMANCE BY PRICE RANGE (QUARTILES)")
    print("=" * 55)

    for i in range(4):
        mask   = (actual >= quartiles[i]) & (actual < quartiles[i + 1])
        a, p   = actual[mask], pred[mask]
        mae_q  = np.mean(np.abs(p - a))
        rmse_q = np.sqrt(np.mean((p - a) ** 2))
        mape_q = np.mean(np.abs((p - a) / a)) * 100

        print()
        print(f"  Range {i + 1}: ${quartiles[i]:,.0f} → ${quartiles[i + 1]:,.0f}")
        print(f"     MAE:  ${mae_q:,.2f}   RMSE: ${rmse_q:,.2f}   MAPE: {mape_q:.2f}%")


# ============================================================
# 9. PREDICTION VISUALIZATIONS
# ============================================================

def plot_predictions(actual_prices, predicted_prices):
    """
    Show 3 charts comparing what the model predicted vs the actual prices:
      1. Scatter plot: predicted vs actual (perfect model = diagonal line)
      2. Histogram of errors (perfect model = narrow spike at 0)
      3. Bar chart comparing 20 random houses side-by-side
    """
    actual = np.array(actual_prices).flatten()
    pred   = np.array(predicted_prices).flatten()

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))

    # 1. Predicted vs Actual scatter
    axes[0].scatter(actual, pred, alpha=0.5, s=10)
    lo = min(actual.min(), pred.min())
    hi = max(actual.max(), pred.max())
    axes[0].plot([lo, hi], [lo, hi], 'r--', linewidth=2, label='Perfect prediction')
    axes[0].set_xlabel('Actual Price ($)')
    axes[0].set_ylabel('Predicted Price ($)')
    axes[0].set_title('Predicted vs Actual Prices')
    axes[0].legend()

    # 2. Residuals histogram
    residuals = pred - actual
    axes[1].hist(residuals, bins=50, color='steelblue', edgecolor='white', alpha=0.7)
    axes[1].axvline(0, color='red', linestyle='--', linewidth=2)
    axes[1].set_xlabel('Prediction Error ($)')
    axes[1].set_ylabel('Frequency')
    axes[1].set_title('Distribution of Prediction Errors')

    # 3. Sample comparison bar chart (20 random houses)
    np.random.seed(42)
    sample_idx = np.random.choice(len(actual), 20, replace=False)
    x_pos, width = np.arange(20), 0.35
    axes[2].bar(x_pos - width / 2, actual[sample_idx], width, label='Actual',    alpha=0.8)
    axes[2].bar(x_pos + width / 2, pred[sample_idx],   width, label='Predicted', alpha=0.8)
    axes[2].set_xlabel('Sample Index')
    axes[2].set_ylabel('Price ($)')
    axes[2].set_title('Sample Predictions vs Actual')
    axes[2].legend()
    axes[2].set_xticks(x_pos)

    plt.tight_layout()
    plt.show()
