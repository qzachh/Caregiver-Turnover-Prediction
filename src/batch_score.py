# src/batch_score.py

import pathlib
import pandas as pd
import datetime as dt
from score import predict_df
from alert import send_alerts
from typing import Optional

# Define paths for the prediction outputs
ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
PROCESSED_DATA_PATH = DATA_DIR / "Caregiver Prediction - Processed_Data.csv"
OUT_PATH = DATA_DIR / f"churn_predictions_{dt.date.today()}.csv"
FILTERED_OUT_PATH = DATA_DIR / f"churn_predictions_filtered_{dt.date.today()}.csv"

def generate_predictions() -> Optional[pathlib.Path]:
    """
    Generates and saves churn predictions.
    Returns the Path to the main predictions file on success, otherwise None.
    """
    try:
        # Step 1: Read the source data and generate predictions
        if not PROCESSED_DATA_PATH.exists():
            print(f"❌ Source data not found at: {PROCESSED_DATA_PATH}")
            return None
            
        now_df = pd.read_csv(PROCESSED_DATA_PATH)
        preds_df = predict_df(now_df)

        # Step 2: Save the initial churn predictions
        preds_df.to_csv(OUT_PATH, index=False)
        print(f"Saved: {OUT_PATH}")

        # Step 3: Filter out caregivers who have already churned and are high risk
        filtered_preds = filter_predictions(now_df, preds_df)

        # Step 4: Save the filtered predictions to a new CSV
        filtered_preds.to_csv(FILTERED_OUT_PATH, index=False)
        print(f"Filtered predictions saved to: {FILTERED_OUT_PATH}")

        # Step 5: Notify HR with the results and file attachments
        send_alerts(filtered_preds, OUT_PATH, FILTERED_OUT_PATH)
        
        # On success, return the path of the created predictions file
        return OUT_PATH
        
    except Exception as e:
        print(f"❌ Error in generate_predictions: {e}")
        return None

def filter_predictions(source_df: pd.DataFrame, pred_df: pd.DataFrame) -> pd.DataFrame:
    """
    Filters predictions to exclude caregivers who have already churned (churn_label == 1)
    and are predicted as HIGH risk.
    """
    # Merge the source data (for 'churn_label') with the prediction data
    merged_df = pred_df.merge(source_df[["caregiver_id", "churn_label"]], on="caregiver_id", how="left")

    # Apply the filter condition
    # The '~' inverts the selection, keeping all rows *except* those that match
    is_excluded = (merged_df["churn_label"] == 1) & (merged_df["risk_level"] == "HIGH")
    filtered_df = merged_df[~is_excluded]

    # Drop the temporary 'churn_label' column before returning
    filtered_df = filtered_df.drop(columns=["churn_label"])

    return filtered_df

if __name__ == "__main__":
    # This part is for direct testing of the module
    saved_file = generate_predictions()
    if saved_file:
        print(f"✅ Predictions generated successfully at: {saved_file}")
    else:
        print("❌ Failed to generate predictions")