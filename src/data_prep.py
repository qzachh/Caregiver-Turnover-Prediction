# Fixed src/data_prep.py

import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer

NUM_COLS = [
    "age", "waiting_days", "total_leave_days",
    "days_worked_2025", "work_ratio_2025", "rank",
    "competency_score", "positive_feedback", "incidents",
    "avg_income_per_shift"
]
CAT_COLS = ["salary_band", "age_band", "home_province"]

TARGET = "churn_label"
TENURE_TARGET = "tenure_days"

def load(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)
    print(f"📊 Loaded CSV with shape: {df.shape}")
    print(f"📋 Columns: {list(df.columns)}")
    
    # Debug: Check tenure_days column
    if TENURE_TARGET in df.columns:
        print(f"🔍 tenure_days info:")
        print(f"  - Data type: {df[TENURE_TARGET].dtype}")
        print(f"  - Unique values sample: {df[TENURE_TARGET].unique()[:10]}")
        print(f"  - NaN count: {df[TENURE_TARGET].isna().sum()}")
        print(f"  - Rows with tenure_days <= 20: {(df[TENURE_TARGET] <= 20).sum()}")
    else:
        print(f"❌ Column '{TENURE_TARGET}' not found in CSV!")
        print(f"Available columns: {list(df.columns)}")
    
    return df

def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    print(f"🧹 Starting clean process with {len(df)} rows")
    
    # Debug: Check tenure_days before filtering
    if TENURE_TARGET in df.columns:
        print(f"🔍 Before filtering - tenure_days stats:")
        print(f"  - Count: {df[TENURE_TARGET].notna().sum()}")
        print(f"  - Min: {df[TENURE_TARGET].min()}")
        print(f"  - Max: {df[TENURE_TARGET].max()}")
        print(f"  - Rows with <= 20: {(df[TENURE_TARGET] <= 20).sum()}")
        
        # Convert to numeric if it's not already (handles string numbers)
        df[TENURE_TARGET] = pd.to_numeric(df[TENURE_TARGET], errors='coerce')
        
        # MAIN FILTER: Remove rows where tenure_days <= 20
        initial_count = len(df)
        df = df[df[TENURE_TARGET] > 20].copy()
        filtered_count = len(df)
        
        print(f"✅ Filtered out {initial_count - filtered_count} rows with tenure_days <= 20")
        print(f"📊 Remaining rows: {filtered_count}")
    else:
        print(f"❌ Cannot filter - '{TENURE_TARGET}' column not found!")
        return df
    
    # Keep rows that have target for churn task
    if TARGET in df.columns:
        before_target_filter = len(df)
        df = df[df[TARGET].notna()]
        after_target_filter = len(df)
        print(f"🎯 Filtered for valid churn labels: {before_target_filter} → {after_target_filter}")
    
    # Basic sanity fixes
    if "age" in df.columns:
        df.loc[df["age"] > 100, "age"] = np.nan
    
    # Fix negative tenure_days (but we already filtered <= 20)
    if TENURE_TARGET in df.columns:
        df.loc[df[TENURE_TARGET] < 0, TENURE_TARGET] = 0
        # Cap at 10 years (3650 days)
        df[TENURE_TARGET] = np.minimum(df[TENURE_TARGET], 3650)
    
    # Derived ratios - FIXED: Use separate variable to avoid modifying tenure_days
    if "days_worked_2025" in df.columns:
        df["is_active_2025"] = (df["days_worked_2025"] > 0).astype(int)
    
    if "total_leave_days" in df.columns and TENURE_TARGET in df.columns:
        # FIXED: Create leave_ratio without modifying tenure_days
        # Use a separate calculation to avoid any side effects
        tenure_for_ratio = df[TENURE_TARGET].fillna(0) + 1  # Add 1 only for this calculation
        df["leave_ratio"] = df["total_leave_days"].fillna(0) / tenure_for_ratio
    
    print(f"✅ Clean process completed. Final shape: {df.shape}")
    
    # VERIFICATION: Check that tenure_days wasn't modified
    if TENURE_TARGET in df.columns:
        print(f"🔍 After cleaning - tenure_days verification:")
        print(f"  - Min: {df[TENURE_TARGET].min()}")
        print(f"  - Max: {df[TENURE_TARGET].max()}")
        print(f"  - Sample values: {df[TENURE_TARGET].head(10).tolist()}")
    
    return df

def make_preprocessor() -> ColumnTransformer:
    num_proc = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", "passthrough")        # keep raw scale for tree models
    ])
    cat_proc = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])
    return ColumnTransformer(
        [("num", num_proc, NUM_COLS + ["is_active_2025", "leave_ratio"]),
         ("cat", cat_proc, CAT_COLS)],
        remainder="drop"
    )