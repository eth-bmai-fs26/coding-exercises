"""
Generate synthetic lead data for training and scoring.
"""
import os
import numpy as np
import pandas as pd

# Set seed for reproducibility
SEED = 42
np.random.seed(SEED)

# Column definitions - only numerical features
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

# Sample sizes
N_TRAIN = 5000
N_SCORE = 200


def generate_features(n_samples):
    """Generate synthetic numerical feature data."""
    data = {
        'company_size': np.random.randint(1, 10000, size=n_samples),
        'pages_viewed_7d': np.random.randint(0, 100, size=n_samples),
        'email_opens_30d': np.random.randint(0, 50, size=n_samples),
        'website_visits_30d': np.random.randint(1, 200, size=n_samples),
        'days_since_signup': np.random.randint(0, 365, size=n_samples),
        'avg_session_duration_min': np.random.uniform(0.5, 60.0, size=n_samples),
        'feature_usage_score': np.random.uniform(0, 100, size=n_samples)
    }
    return pd.DataFrame(data)


def generate_target(df):
    """
    Generate conversion labels using a logistic function.
    Higher scores for: large companies, high engagement, long sessions, etc.
    """
    # Normalize features to 0-1 scale
    company_norm = np.log1p(df['company_size']) / np.log1p(10000)
    pages_norm = df['pages_viewed_7d'] / 100.0
    email_norm = df['email_opens_30d'] / 50.0
    visits_norm = df['website_visits_30d'] / 200.0
    days_norm = df['days_since_signup'] / 365.0
    session_norm = df['avg_session_duration_min'] / 60.0
    feature_norm = df['feature_usage_score'] / 100.0

    # Build logit score
    logit = (
        2.0 * company_norm +
        3.0 * pages_norm +
        2.0 * email_norm +
        2.5 * visits_norm +
        -1.5 * days_norm +  # Negative: newer leads score higher
        1.8 * session_norm +
        3.5 * feature_norm +
        -4.0  # baseline bias
    )

    # Add noise
    noise = np.random.normal(0, 0.5, size=len(df))
    logit += noise

    # Convert to probability
    prob = 1 / (1 + np.exp(-logit))

    # Sample binary outcome
    converted = np.random.binomial(1, prob)

    return converted


def main():
    """Generate training and scoring datasets."""
    # Create data directory
    os.makedirs('data', exist_ok=True)

    print("Generating training data...")
    train_df = generate_features(N_TRAIN)
    train_df[TARGET] = generate_target(train_df)

    # Save training data
    train_path = 'data/leads_train.csv'
    train_df.to_csv(train_path, index=False)
    print(f"Saved {len(train_df)} training samples to {train_path}")
    print(f"Conversion rate: {train_df[TARGET].mean():.2%}")

    # Generate scoring data (without target)
    print("\nGenerating scoring data...")
    score_df = generate_features(N_SCORE)

    # Save scoring data
    score_path = 'data/leads_to_score.csv'
    score_df.to_csv(score_path, index=False)
    print(f"Saved {len(score_df)} samples to {score_path}")

    print("\nColumn summary:")
    print(f"  Numerical features: {NUM_COLS}")
    print(f"  Target: {TARGET}")
    print("\nData generation complete!")


if __name__ == '__main__':
    main()
