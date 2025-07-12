
# Caregiver Churn Prediction Automation - Setup Guide

## 📋 Overview

This automation system allows users to run churn prediction models, without needing to manually download CSV files or use VSCode.

## 🚀 Quick Start (For Non-Technical Users)

### Windows Users:

1.  **Double-click** `install_requirements.bat` (only needed once).
2.  **Double-click** `run_automation.bat` (for command-line) or `run_automation_gui.bat` (for the user interface).
3.  **Wait** for the automation to complete.
4.  **Check** the `data` folder for your prediction results.

### Mac/Linux Users:

Running the automation on macOS or Linux requires using the Terminal.

1.  **Open the Terminal** application.
2.  Type ` cd  ` (with a space after `cd`) into the Terminal window.
3.  **Drag and drop** the `wecare_churn` folder from your Finder/File Explorer directly into the Terminal window. The path to the folder will appear.
4.  Press **Enter**. You are now in the correct directory.
5.  Type `./run_automation.sh` and press **Enter**. The script will first install any missing requirements and then run the automation.
6.  **Wait** for the automation to complete.
7.  **Check** the `data` folder for your prediction results.

## 📁 Project Structure

```
wecare_churn/
├── main.py                     ← Main automation script (command line)
├── main_gui.py                 ← GUI version with a button
├── config.json                 ← Configuration settings
├── requirements.txt            ← Python dependencies
├── run_automation.bat          ← Windows batch file
├── run_automation_gui.bat      ← Windows GUI batch file
├── run_automation.sh           ← Mac/Linux shell script
├── install_requirements.bat    ← Install dependencies (Windows)
├── SETUP_GUIDE.md              ← This file
├── USER_MANUAL.md              ← User manual
├── data/                       ← Output folder
│   ├── Caregiver Prediction - Processed_Data.csv
│   ├── churn_predictions_{date}.csv       ← Final predictions
│   ├── churn_predictions_filtered_{date}.csv ← Filtered predictions
│   └── automation_log.txt      ← Detailed logs
├── models/                     ← Trained models
│   ├── churn_model.joblib
│   └── tenure_model.joblib
└── src/                        ← Source code
    ├── __init__.py
    ├── config.py
    ├── data_prep.py
    ├── train_churn.py
    ├── train_tenure.py
    ├── batch_score.py
    ├── api.py
    └── alert.py
```

## ⚙️ Initial Setup (One-Time Only)

### Step 1: Configure Google Sheets Access

1.  **Open** `config.json` in a text editor.
2.  **Replace** the placeholder values for `"sheet_id"` and `"gid"` with your actual Google Sheet ID and Tab ID.

### Step 2: Find Your Google Sheet ID and GID

  * **Sheet ID**: In your Google Sheet URL (`https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit#gid=[GID]`), copy the long string of characters that constitutes the `[SHEET_ID]`.
  * **GID (Tab ID)**: From the same URL, copy the number after `gid=`. If `gid=` is not visible, the default is `0`.

### Step 3: Test the Connection

1.  Run the automation once to test if it can fetch the data.
2.  Check if `Caregiver Prediction - Processed_Data.csv` is created in the `data` folder.
3.  If it fails, double-check your Sheet ID and GID in the `config.json` file.

## 💻 Propagating the Prediction Models

To use the trained prediction models on another computer without re-training, follow these steps:

1.  **On the original computer**, locate the `wecare_churn` folder.
2.  Inside this folder, find the `models` directory.
3.  **Copy the entire `models` folder**. This folder contains the `churn_model.joblib` and `tenure_model.joblib` files, which are the trained prediction models.
4.  **On the new computer**, place the copied `models` folder into the main `wecare_churn` directory.

The automation will now use these pre-trained models to generate predictions without needing to perform the training steps.

## 📊 Understanding the Output

After successful automation, you'll find these files in the `data` folder:

1.  **`churn_predictions_{date}.csv`**: Main output with predictions for all caregivers.
2.  **`churn_predictions_filtered_{date}.csv`**: Output excluding caregivers who have already churned and were at high risk.
3.  **`automation_log.txt`**: Detailed logs of the automation process.
4.  **`Caregiver Prediction - Processed_Data.csv`**: The raw data downloaded from Google Sheets.

### Sample Prediction Output:

The output file `churn_predictions_{date}.csv` will have the following columns:

| caregiver\_id | churn\_probability | risk\_level | days\_to\_quit\_est | estimated\_quit\_date |
| :--- | :--- | :--- | :--- | :--- |
| WC-1840 | 70.19 | HIGH | 5 | 2025-07-17 |