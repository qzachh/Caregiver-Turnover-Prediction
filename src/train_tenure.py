# src/train_tenure.py
import joblib, pathlib, numpy as np, pandas as pd
from lifelines import CoxPHFitter
from data_prep import load, clean, make_preprocessor, TENURE_TARGET
from scipy.sparse import issparse

ROOT      = pathlib.Path(__file__).resolve().parents[1]
DATA      = ROOT / "data" / "Caregiver Prediction - Processed_Data.csv"
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(exist_ok=True)

# ------------------------------------------------------------------
def train_tenure_model():
    try:
        df = clean(load(str(DATA)))

        # ---------- SURVIVAL LABELS ----------
        df["event"] = df["churn_label"].astype(int)                   # 1 = quit, 0 = censored
        df["log_current_tenure"] = np.log1p(df["tenure_days"])        # <<< NEW feature

        surv_df = df.dropna(subset=["event"]).copy()

        # ---------- FEATURES ----------
        base_features = surv_df.drop(
            columns=["caregiver_id", "churn_label", TENURE_TARGET, "event"]
        )

        pre = make_preprocessor()
        pre.fit(base_features)

        X = pre.transform(base_features)
        if issparse(X):
            X = X.toarray()

        feature_names = pre.get_feature_names_out()
        X = pd.DataFrame(X, columns=feature_names, index=surv_df.index)

        # append duration + event
        X[TENURE_TARGET] = surv_df[TENURE_TARGET]
        X["event"] = surv_df["event"]

        # ---------- LOW-VARIANCE + MULTICOLLINEARITY CLEAN-UP ----------
        feat_cols = [c for c in X.columns if c not in (TENURE_TARGET, "event")]

        # remove near-constant
        low_var = [c for c in feat_cols if X[c].var() < 1e-10]
        if low_var:
            print("Removing low-variance:", low_var)
            X.drop(columns=low_var, inplace=True)

        # remove highly correlated
        corr = X[feat_cols].corr().abs()
        high_corr = [
            b
            for a in corr.columns
            for b in corr.index
            if a != b and corr.loc[a, b] > 0.95 and b not in feat_cols[: feat_cols.index(a)]
        ]
        if high_corr:
            print("Removing high corr:", high_corr)
            X.drop(columns=high_corr, inplace=True)

        # ---------- FIT COXPH ----------
        cph = CoxPHFitter(penalizer=1.0, l1_ratio=0.3, alpha=0.95)
        cph.fit(X, duration_col=TENURE_TARGET, event_col="event")

        print(cph.summary.head())

        # ---------- SANITY CHECK ----------
        med_pred = cph.predict_median(X.drop(columns=[TENURE_TARGET, "event"]).head(5))
        print("Sample medians:", med_pred.values)

        # ---------- SAVE ----------
        joblib.dump({"model": cph, "pre": pre}, MODEL_DIR / "tenure_model.joblib")
        print("✅ tenure_model.joblib saved")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in tenure model training: {e}")
        return False

# ------------------------------------------------------------------
if __name__ == "__main__":
    success = train_tenure_model()
    if success:
        print("✅ Tenure model saved successfully")
    else:
        print("❌ Tenure model training failed")