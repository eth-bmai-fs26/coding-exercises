"""
Streamlit app for lead scoring.
"""
import os
import json
import pandas as pd
import joblib
import torch
import streamlit as st

from model import LeadScoringMLP


@st.cache_resource
def load_artifacts():
    """Load trained model and preprocessor."""
    artifacts_dir = 'artifacts'

    # Check if artifacts exist
    required_files = ['model.pt', 'preprocessor.joblib', 'meta.json']
    missing = [f for f in required_files if not os.path.exists(os.path.join(artifacts_dir, f))]

    if missing:
        st.error(f"Missing artifacts: {', '.join(missing)}")
        st.info("Please run the following commands first:\n```\npython generate_data.py\npython train.py\n```")
        st.stop()

    # Load metadata
    with open(os.path.join(artifacts_dir, 'meta.json'), 'r') as f:
        meta = json.load(f)

    # Load preprocessor
    preprocessor = joblib.load(os.path.join(artifacts_dir, 'preprocessor.joblib'))

    # Load model
    model = LeadScoringMLP(meta['input_dim'], meta['hidden_dim'])
    model.load_state_dict(torch.load(os.path.join(artifacts_dir, 'model.pt')))
    model.eval()

    return model, preprocessor, meta


def assign_tier(score):
    """Assign tier based on score."""
    if score < 0.33:
        return 'low'
    elif score < 0.66:
        return 'medium'
    else:
        return 'high'


def score_leads(df, model, preprocessor, meta):
    """Score leads and add tier."""
    required_cols = meta['num_cols']

    # Check for missing columns
    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        st.error(f"Missing required columns: {', '.join(missing_cols)}")
        return None

    # Prepare features
    X = df[required_cols]
    X_transformed = preprocessor.transform(X)

    # Run inference
    with torch.no_grad():
        X_tensor = torch.FloatTensor(X_transformed)
        logits = model(X_tensor)
        probs = torch.sigmoid(logits).numpy()

    # Add scores to dataframe
    result_df = df.copy()
    result_df['lead_score'] = probs
    result_df['lead_tier'] = result_df['lead_score'].apply(assign_tier)

    return result_df


def main():
    """Main Streamlit app."""
    st.set_page_config(page_title="Lead Scoring App", page_icon="📊")

    st.title("📊 Lead Scoring App")

    # Load artifacts
    model, preprocessor, meta = load_artifacts()

    # File upload
    uploaded_file = st.file_uploader("Upload CSV file", type=['csv'])

    if uploaded_file is not None:
        # Load and score CSV
        df = pd.read_csv(uploaded_file)
        scored_df = score_leads(df, model, preprocessor, meta)

        if scored_df is not None:
            # Show top leads
            st.subheader("Top 25 Leads by Score")
            top_leads = scored_df.nlargest(25, 'lead_score')
            st.dataframe(top_leads, use_container_width=True, hide_index=True)

            # Download button
            csv = scored_df.to_csv(index=False)
            st.download_button(
                label="Download Scored CSV",
                data=csv,
                file_name="leads_scored.csv",
                mime="text/csv"
            )


if __name__ == '__main__':
    main()
