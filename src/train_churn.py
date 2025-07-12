# src/train_churn.py
import joblib, pathlib, json
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.metrics import roc_auc_score, classification_report
from data_prep import load, clean, make_preprocessor, TARGET

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "Caregiver Prediction - Processed_Data.csv"
MODEL_DIR = ROOT / "models"
MODEL_DIR.mkdir(exist_ok=True)

def train_churn_model():
    try:
        # Convert DATA (Path object) to a string using str() before passing it to load()
        df = clean(load(str(DATA)))

        X = df.drop(columns=[TARGET, "caregiver_id"])
        y = df[TARGET]

        pre = make_preprocessor()
        X_pre = pre.fit_transform(X)

        # model
        clf = GradientBoostingClassifier(random_state=42)
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        auc = cross_val_score(clf, X_pre, y, cv=cv, scoring="roc_auc")
        print(f"5-fold AUC: {auc.mean():.3f} ± {auc.std():.3f}")

        # final fit + hold-out
        X_train, X_test, y_train, y_test = train_test_split(
            X_pre, y, test_size=0.2, stratify=y, random_state=42
        )
        clf.fit(X_train, y_train)
        preds = clf.predict_proba(X_test)[:, 1]
        print(classification_report(y_test, preds > 0.5, digits=3))
        print("Hold-out AUC:", roc_auc_score(y_test, preds))

        joblib.dump({"model": clf, "pre": pre, "features": X.columns.tolist()},
                    MODEL_DIR / "churn_model.joblib")
        
        print("✅ Churn model training completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error in churn model training: {e}")
        return False

if __name__ == "__main__":
    success = train_churn_model()
    if success:
        print("✅ Churn model saved successfully")
    else:
        print("❌ Churn model training failed")
