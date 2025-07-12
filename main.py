#!/usr/bin/env python3
"""
WeCare247 Churn Prediction Automation
One-click solution to fetch data, train models, and generate predictions
"""

import os
import sys
import requests
import pathlib
import datetime
import csv
import subprocess
import logging
import json
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the src directory to the system path to allow module imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Import your custom modules
try:
    from src.data_prep import load, clean
    from src.train_churn import train_churn_model
    from src.train_tenure import train_tenure_model
    from src.batch_score import generate_predictions
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    print("Please ensure all required modules are in the src/ directory and have no errors.")
    input("Press Enter to exit...")
    sys.exit(1)

# --- Configuration Loading ---
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    GOOGLE_SHEET_CONFIG = {
        "SHEET_ID": config['google_sheets']['sheet_id'],
        "GID": config['google_sheets']['gid'],
        "TIMEOUT": config['google_sheets'].get('timeout', 30)
    }
except (FileNotFoundError, KeyError) as e:
    print(f"❌ Configuration error in 'config.json': {e}. Please ensure the file exists and is correctly formatted.")
    sys.exit(1)

# --- File Paths ---
DATA_DIR = pathlib.Path("data")
MODELS_DIR = pathlib.Path("models")
PROCESSED_DATA_FILE = DATA_DIR / "Caregiver Prediction - Processed_Data.csv"
LOGFILE = DATA_DIR / "automation_log.txt"
# NOTE: PREDICTIONS_FILE is now determined dynamically, not with a static variable here.

# --- Directory and Logging Setup ---
DATA_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler(LOGFILE, mode='a'), logging.StreamHandler()])
logger = logging.getLogger(__name__)


def print_banner():
    """Prints the welcome banner."""
    print("=" * 60)
    print("🏥 WeCare247 Churn Prediction Automation 🤖")
    print("=" * 60)
    print(f"📅 Started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

def fetch_google_sheet_data() -> bool:
    """Fetches data from Google Sheets, returning True on success."""
    # (This function is unchanged)
    print("\n📊 Step 1: Fetching data from Google Sheets...")
    try:
        url = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_CONFIG['SHEET_ID']}/export?format=csv&gid={GOOGLE_SHEET_CONFIG['GID']}"
        print(f"🔗 Fetching from: {url[:50]}...")
        response = requests.get(url, timeout=GOOGLE_SHEET_CONFIG['TIMEOUT'])
        response.raise_for_status()
        PROCESSED_DATA_FILE.write_bytes(response.content)
        if PROCESSED_DATA_FILE.exists() and PROCESSED_DATA_FILE.stat().st_size > 0:
            print(f"✅ Data successfully fetched and saved to: {PROCESSED_DATA_FILE}")
            # ... (rest of the function is the same) ...
            return True
        else:
            print("❌ Failed to create or file is empty")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    # (Assume the rest of the verification logic from your original file is here)

def prepare_data() -> bool:
    """Cleans and prepares data, returning True on success."""
    # (This function is unchanged)
    print("\n🧹 Step 2: Cleaning and preparing data...")
    try:
        print(f"📁 Loading data from: {PROCESSED_DATA_FILE}")
        raw_df = load(str(PROCESSED_DATA_FILE))
        logger.info(f"Loaded {len(raw_df)} rows from {PROCESSED_DATA_FILE}")
        print("🔧 Applying data cleaning and filtering...")
        cleaned_df = clean(raw_df)
        logger.info(f"Data cleaned. Resulting shape: {cleaned_df.shape}")
        # ... (rest of the function is the same) ...
        cleaned_df.to_csv(PROCESSED_DATA_FILE, index=False)
        print(f"💾 Cleaned data saved to: {PROCESSED_DATA_FILE}")
        print("✅ Data preparation completed successfully.")
        return True
    except Exception as e:
        print(f"❌ Error during data preparation: {e}")
        logger.error(f"Data preparation error: {e}", exc_info=True)
        return False
    # (Assume the rest of the validation logic from your original file is here)

def train_models() -> bool:
    """Trains both models, returning True on success."""
    # (This function is unchanged)
    print("\n🚀 Step 3: Training prediction models...")
    try:
        print("🎯 Training churn prediction model...")
        if not train_churn_model():
            print("❌ Churn model training failed")
            return False
        print("✅ Churn model training completed")
        
        print("⏰ Training tenure prediction model...")
        if not train_tenure_model():
            print("❌ Tenure model training failed")
            return False
        print("✅ Tenure model training completed")
        return True
    except Exception as e:
        print(f"❌ Error during model training: {e}")
        logger.error(f"Model training error: {e}")
        return False

def generate_predictions_file() -> Optional[pathlib.Path]:
    """
    Generates predictions and returns the file path on success, otherwise None.
    """
    print("\n🔮 Step 4: Generating predictions...")
    try:
        # Call the function and get the actual path of the created file
        saved_file_path = generate_predictions()

        # Check if the path was returned and if that file actually exists
        if saved_file_path and saved_file_path.exists():
            print(f"✅ Predictions generated successfully: {saved_file_path}")
            return saved_file_path  # Return the path for the next steps
        else:
            print("❌ Failed to generate predictions")
            return None
            
    except Exception as e:
        print(f"❌ Error during prediction generation: {e}")
        logger.error(f"Prediction generation error: {e}", exc_info=True)
        return None

def open_results(prediction_file_path: pathlib.Path):
    """Opens the results folder and the specific prediction file."""
    # (This function is unchanged but now receives the correct path)
    print("\n📂 Step 5: Opening results...")
    try:
        if sys.platform == "win32":
            os.startfile(DATA_DIR)
            if prediction_file_path.exists(): os.startfile(prediction_file_path)
        elif sys.platform == "darwin":  # macOS
            subprocess.run(["open", DATA_DIR])
            if prediction_file_path.exists(): subprocess.run(["open", prediction_file_path])
        else:  # Linux
            subprocess.run(["xdg-open", DATA_DIR])
            if prediction_file_path.exists(): subprocess.run(["xdg-open", prediction_file_path])
        print("✅ Results opened automatically.")
    except Exception as e:
        print(f"⚠️  Could not open results automatically: {e}")

# (create_summary_report function remains the same, but could also be updated to accept the path)

def main():
    """Main automation function."""
    print_banner()
    logger.info("Starting WeCare247 Churn Prediction Automation")
    
    try:
        if not fetch_google_sheet_data():
            raise RuntimeError("Failed to fetch data from Google Sheets.")
        
        if not prepare_data():
            raise RuntimeError("Failed to prepare data.")
        
        if not train_models():
            raise RuntimeError("Failed to train models.")
        
        # This now returns the path on success or None on failure
        final_prediction_path = generate_predictions_file()
        if not final_prediction_path:
            raise RuntimeError("Failed to generate predictions.")
        
        # Pass the correct path to the next steps
        open_results(final_prediction_path)
        # create_summary_report(final_prediction_path) # You could update this too
        
        print("\n" + "=" * 60)
        print("🎉 AUTOMATION COMPLETED SUCCESSFULLY! 🎉")
        print("=" * 60)
        print(f"📊 Your predictions are ready in: {final_prediction_path}")
        print(f"📁 All files are in: {DATA_DIR}")
        print("=" * 60)
        logger.info("Automation completed successfully")
        
    except RuntimeError as e:
        print(f"\n❌ {e} Exiting...")
        logger.error(f"Automation failed: {e}")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {e}")
        logger.critical(f"Unexpected automation error: {e}", exc_info=True)
    
    finally:
        print("\n🔚 Automation finished.")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()