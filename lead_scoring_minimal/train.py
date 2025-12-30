"""
Train a PyTorch MLP for lead scoring with early stopping.
"""
import os
import json
import numpy as np
import pandas as pd
import joblib
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import roc_auc_score

from model import LeadScoringMLP

# Set seeds
SEED = 42
np.random.seed(SEED)
torch.manual_seed(SEED)

# Column definitions (must match generate_data.py)
NUM_COLS = [
    'company_size',
    'pages_viewed_7d',
    'email_opens_30d',
    'website_visits_30d',
    'days_since_signup',
    'avg_session_duration_min',
    'feature_usage_score'
]
TARGET = 'converted'

# Hyperparameters
TEST_SIZE = 0.2
HIDDEN_DIM = 64
BATCH_SIZE = 64
LEARNING_RATE = 0.001
N_EPOCHS = 100
PATIENCE = 8


def prepare_data(df, preprocessor=None, fit=False):
    """Prepare features and optionally fit preprocessor."""
    X = df[NUM_COLS]

    if fit:
        # Create and fit preprocessor (StandardScaler for all numerical features)
        preprocessor = StandardScaler()
        X_transformed = preprocessor.fit_transform(X)
    else:
        X_transformed = preprocessor.transform(X)

    return X_transformed, preprocessor


def train_epoch(model, X_train, y_train, optimizer, criterion):
    """Train for one epoch."""
    model.train()

    # Create batches
    n_samples = len(X_train)
    indices = np.random.permutation(n_samples)
    total_loss = 0.0
    n_batches = 0

    for start_idx in range(0, n_samples, BATCH_SIZE):
        end_idx = min(start_idx + BATCH_SIZE, n_samples)
        batch_indices = indices[start_idx:end_idx]

        X_batch = torch.FloatTensor(X_train[batch_indices])
        y_batch = torch.FloatTensor(y_train[batch_indices])

        # Forward pass
        optimizer.zero_grad()
        logits = model(X_batch)
        loss = criterion(logits, y_batch)

        # Backward pass
        loss.backward()
        optimizer.step()

        total_loss += loss.item()
        n_batches += 1

    return total_loss / n_batches


def evaluate(model, X_val, y_val):
    """Evaluate model and return AUC."""
    model.eval()

    with torch.no_grad():
        X_tensor = torch.FloatTensor(X_val)
        logits = model(X_tensor)
        probs = torch.sigmoid(logits).numpy()

    auc = roc_auc_score(y_val, probs)
    return auc


def main():
    """Main training pipeline."""
    # Create artifacts directory
    os.makedirs('artifacts', exist_ok=True)

    print("Loading training data...")
    df = pd.read_csv('data/leads_train.csv')
    print(f"Loaded {len(df)} samples")
    print(f"Conversion rate: {df[TARGET].mean():.2%}")

    # Split data
    print("\nSplitting data...")
    train_df, val_df = train_test_split(
        df,
        test_size=TEST_SIZE,
        stratify=df[TARGET],
        random_state=SEED
    )
    print(f"Train: {len(train_df)}, Val: {len(val_df)}")

    # Prepare features
    print("\nPreparing features...")
    X_train, preprocessor = prepare_data(train_df, fit=True)
    X_val, _ = prepare_data(val_df, preprocessor=preprocessor, fit=False)

    y_train = train_df[TARGET].values
    y_val = val_df[TARGET].values

    input_dim = X_train.shape[1]
    print(f"Input dimension: {input_dim}")

    # Create model
    print("\nInitializing model...")
    model = LeadScoringMLP(input_dim, hidden_dim=HIDDEN_DIM)
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Training loop with early stopping
    print("\nTraining...")
    best_auc = 0.0
    patience_counter = 0
    best_state = None

    for epoch in range(1, N_EPOCHS + 1):
        train_loss = train_epoch(model, X_train, y_train, optimizer, criterion)
        val_auc = evaluate(model, X_val, y_val)

        # Print progress every 5 epochs
        if epoch % 5 == 0 or epoch == 1:
            print(f"Epoch {epoch:3d}/{N_EPOCHS} | Loss: {train_loss:.4f} | Val AUC: {val_auc:.4f}")

        # Early stopping check
        if val_auc > best_auc:
            best_auc = val_auc
            patience_counter = 0
            best_state = model.state_dict().copy()
        else:
            patience_counter += 1

        if patience_counter >= PATIENCE:
            print(f"\nEarly stopping at epoch {epoch}")
            break

    # Restore best model
    if best_state is not None:
        model.load_state_dict(best_state)

    print(f"\nBest validation AUC: {best_auc:.4f}")

    # Save artifacts
    print("\nSaving artifacts...")

    # Save model
    model_path = 'artifacts/model.pt'
    torch.save(model.state_dict(), model_path)
    print(f"Saved model to {model_path}")

    # Save preprocessor
    preprocessor_path = 'artifacts/preprocessor.joblib'
    joblib.dump(preprocessor, preprocessor_path)
    print(f"Saved preprocessor to {preprocessor_path}")

    # Save metadata
    meta = {
        'target': TARGET,
        'num_cols': NUM_COLS,
        'input_dim': input_dim,
        'hidden_dim': HIDDEN_DIM,
        'best_val_auc': float(best_auc)
    }
    meta_path = 'artifacts/meta.json'
    with open(meta_path, 'w') as f:
        json.dump(meta, f, indent=2)
    print(f"Saved metadata to {meta_path}")

    print("\nTraining complete!")


if __name__ == '__main__':
    main()
