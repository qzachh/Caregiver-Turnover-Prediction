import joblib, pathlib, pandas as pd, numpy as np, math          # <<< NEW (math)
from datetime import timedelta, date                             # <<< NEW (date)
from config import HIGH, MEDIUM
from scipy.sparse import issparse

ROOT        = pathlib.Path(__file__).resolve().parents[1]
MODEL_DIR    = ROOT / "models"
THRESHOLDS   = {"HIGH": HIGH, "MEDIUM": MEDIUM}

# ------------------------------------------------------------------
# Load once
churn_bundle  = joblib.load(MODEL_DIR / "churn_model.joblib")
tenure_bundle = joblib.load(MODEL_DIR / "tenure_model.joblib")

TODAY = date.today()                                             # <<< NEW

def _risk(prob: float) -> str:
    if prob >= THRESHOLDS["HIGH"]:
        return "HIGH"
    if prob >= THRESHOLDS["MEDIUM"]:
        return "MEDIUM"
    return "LOW"

# ------------------------------------------------------------------
def predict_single(cg: dict) -> dict:
    """
    Predict churn and tenure for a single caregiver.
    """

    # ---------- 1 · BASIC FEATURES ----------
    X_raw = pd.DataFrame([cg])

    tenure_days = cg.get("tenure_days", 0)
    X_raw["leave_ratio"]   = (
        cg.get("total_leave_days", 0) / tenure_days if tenure_days > 0 else 0
    )
    X_raw["is_active_2025"] = 1 if cg.get("days_worked_2025", 0) > 0 else 0

    # ---------- 2 · CHURN ----------
    try:
        X_churn = churn_bundle["pre"].transform(X_raw)
        X_churn = X_churn.toarray() if issparse(X_churn) else X_churn.values
        prob        = float(churn_bundle["model"].predict_proba(X_churn)[0, 1])
    except Exception as e:
        print(f"❌ Churn prediction error for {cg.get('caregiver_id','?')}: {e}")
        prob = 0.0

    risk_level = _risk(prob)

    # --- PRESENTATION SCALE -------------------------------------
    prob_pct = round(prob * 100, 3)              # 0–100 with 3 dp
    # -------------------------------------------------------------

        # ---------- 3 · TENURE ----------
    try:
        X_tenure = tenure_bundle["pre"].transform(X_raw)
        X_tenure = X_tenure.toarray() if issparse(X_tenure) else X_tenure.values

        try:
            feat_names = tenure_bundle["pre"].get_feature_names_out()
        except AttributeError:
            feat_names = [f"f_{i}" for i in range(X_tenure.shape[1])]

        # lifelines may return Series *or* scalar
        pred = tenure_bundle["model"].predict_median(
            pd.DataFrame(X_tenure, columns=feat_names)
        )

        if isinstance(pred, (pd.Series, pd.DataFrame)):
            est_total = float(pred.iloc[0])
        else:                          # numpy.float64 or plain float
            est_total = float(pred)

        if not np.isfinite(est_total) or est_total <= 0:
            raise ValueError("invalid est_total")

    except Exception as e:
        print(f"❌ Tenure prediction error for {cg.get('caregiver_id','?')}: {e}")
        est_total = tenure_days + 365  # fallback


    # ---------- 4 · REMAINING DAYS ----------
    remaining = max(est_total - tenure_days, 0.0)
    if not np.isfinite(remaining) or remaining > 36500:
        remaining = 365

    # ---------- 5 · PRESENTATION RULE ----------  # <<< NEW BLOCK
    if (risk_level == "LOW") or (remaining < 0.5):
        days_to_quit_est    = "-"      
        estimated_quit_date = "-"
    else:
        days_to_quit_est    = int(math.ceil(remaining))  # 0.4 → 1
        estimated_quit_date = (TODAY + timedelta(days=days_to_quit_est)).isoformat()
    # -----------------------------------------------------------

    return {
        "caregiver_id":        cg.get("caregiver_id", "UNKNOWN"),
        "churn_probability":   prob_pct,
        "risk_level":          risk_level,
        "days_to_quit_est":    days_to_quit_est,
        "estimated_quit_date": estimated_quit_date,
    }

# ------------------------------------------------------------------
# Bulk helper
def predict_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply predict_single() to every row of a DataFrame and
    return the combined results as a new DataFrame.
    Keeps the old signature so batch_score.py continues to work.
    """
    records = []
    total = len(df)
    print(f"🔮 Scoring {total} caregivers…")

    for i, (_, row) in enumerate(df.iterrows(), start=1):
        try:
            records.append(predict_single(row.to_dict()))
        except Exception as e:
            print(f"❌ row {i}: {e}")
            records.append(
                {
                    "caregiver_id": row.get("caregiver_id", f"ERROR_{i}"),
                    "churn_probability": np.nan,
                    "risk_level": "ERROR",
                    "days_to_quit_est": None,
                    "estimated_quit_date": None,
                    "error": str(e),
                }
            )

        if i % 100 == 0 or i == total:
            print(f"   …{i}/{total}")

    return pd.DataFrame(records)
