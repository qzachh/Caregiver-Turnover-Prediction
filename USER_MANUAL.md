
# Caregiver Churn Prediction - User Manual

## 🎯 What This Does

This automation automatically:

1.  **Fetches** the latest caregiver data from Google Sheets.
2.  **Cleans** and prepares the data.
3.  **Trains** new prediction models or uses existing ones.
4.  **Generates** churn predictions for all caregivers.
5.  **Saves** the results as a CSV file that you can open in Excel.

## 🚀 How to Use (Simple Steps)

### For Windows Users:

1.  **Double-click** `run_automation.bat` or the user-friendly `run_automation_gui.bat`.
2.  **Wait** for the process to complete (this may take 2-5 minutes).
3.  **Look** for the success message in the window.
4.  **Open** the `data` folder to find your results.

### For Mac/Linux Users:

1.  **Open the Terminal**.
2.  Type ` cd  ` (with a space), then drag the **`wecare_churn` folder** into the terminal window and press **Enter**.
3.  Type `./run_automation.sh` and press **Enter** to start the process.
4.  After the script finishes, **check the `data` folder** for the prediction files.

### For GUI Version (All Systems):

1.  Run `run_automation_gui.bat` (Windows) or `python3 main_gui.py` (Mac/Linux).
2.  Click the **"🚀 Run Automation"** button.
3.  Watch the progress in the log window.
4.  Click **"📂 Open Results"** when the process is complete.

## 📊 Understanding Your Results

### Main Output File: `churn_predictions_{date}.csv`

This file contains the churn predictions for each caregiver, with the following columns:

| Column | Description | Example |
| :--- | :--- | :--- |
| `caregiver_id` | The unique ID for the caregiver. | WC-1840 |
| `churn_probability` | The likelihood the caregiver will leave, as a percentage. | 70.19 |
| `risk_level` | The assigned risk category based on the churn probability. | HIGH |
| `days_to_quit_est` | An estimate of how many days remain before the caregiver quits. | 5 |
| `estimated_quit_date`| The projected date of departure based on the estimate. | 2025-07-17 |

### Risk Levels:

  - **HIGH**: Caregivers with a high probability of churning soon; these require immediate attention.
  - **MEDIUM**: Caregivers with a moderate risk of churning; these should be monitored.
  - **LOW**: Caregivers who are currently stable and at a low risk of leaving.

## 📈 Using the Predictions

### For HR/Management:

  - **Focus** on caregivers in the **HIGH** risk category first.
  - **Schedule** retention interviews or check-ins with caregivers in the **MEDIUM** risk category.
  - **Acknowledge** and continue to support top-performing caregivers in the **LOW** risk category to maintain morale.

### For Operational Planning:
- **Prepare** recruitment for HIGH risk positions
- **Plan** training for potential replacements
- **Adjust** workload distribution

### For Reporting:
- **Track** risk level trends over time
- **Measure** prediction accuracy
- **Report** retention metrics to leadership


-----

## 📁 File Locations

After running automation, check these folders:

```
wecare_churn/
├── data/
│   ├── churn_predictions.csv      ← 🎯 Your main results
│   ├── automation_log.txt         ← Detailed logs
│   ├── automation_report.txt      ← Summary
│   └── Caregiver Prediction...   ← Raw data
└── models/
    ├── churn_model.joblib         ← Trained model
    └── tenure_model.joblib        ← Trained model
```

-----

## 🔄 Regular Usage Schedule

### Recommended Frequency:
- **Weekly**: For active monitoring
- **Monthly**: For reporting and planning
- **As needed**: Before important meetings or reviews

### Best Practices:
1. **Run** early in the morning for fresh data
2. **Check** the log file if anything seems unusual
3. **Backup** important prediction files
4. **Share** results with relevant team members

-----

## ⚠️ What to Do If Something Goes Wrong

### Common Issues and Solutions:

#### 1. Automation Won't Start
**Try:**
- Right-click → "Run as administrator" (Windows)
- Check if Python is installed
- Run `install_requirements.bat` first

#### 2. "Can't Fetch Data" Error
**Try:**
- Check internet connection
- Verify Google Sheet is accessible
- Contact IT to check Sheet ID in config.json

#### 3. No Predictions Generated
**Try:**
- Check if there's enough data (need at least 100 records)
- Look at `automation_log.txt` for specific errors
- Contact technical support

#### 4. Predictions Look Strange
**Check:**
- Are all caregivers showing the same risk level?
- Do the numbers make sense based on recent hires?
- Compare with previous predictions

### Emergency Fallback:
If automation completely fails, you can:
1. **Manually download** the CSV from Google Sheets
2. **Contact** your IT support
3. **Use** the previous week's predictions temporarily

-----

## 🔧 Maintenance

### Monthly Tasks:
- **Run** automation to refresh predictions
- **Review** prediction accuracy
- **Update** any caregiver information in Google Sheets

### Quarterly Tasks:
- **Check** if automation is working properly
- **Backup** important files
- **Review** this manual for updates

-----

## 📞 Getting Help

### When to Contact Support:
- Automation fails multiple times
- Predictions seem consistently wrong
- Need to change Google Sheet source
- Want to modify prediction criteria

### What to Include When Asking for Help:
1. **Error message** (exact text)
2. **Log file** (`automation_log.txt`)
3. **What you were trying to do**
4. **When the problem started**

### Quick Self-Help:
1. **Check** `automation_log.txt` for clues
2. **Try** running again (sometimes it's just a network issue)
3. **Restart** your computer if problems persist
4. **Use** the GUI version to see real-time progress

-----

## 💡 Tips for Success

1. **Run regularly** - Weekly is ideal
2. **Keep data clean** - Update Google Sheets regularly
3. **Act on predictions** - Use HIGH risk alerts quickly
4. **Track results** - Note which predictions were accurate
5. **Share insights** - Help other departments understand the data

-----

## 🎯 Key Reminders

- **Results are predictions, not guarantees**
- **Use alongside human judgment**
- **Focus on trends, not single predictions**
- **Update source data regularly**
- **Keep the automation running consistently**

---

**Questions?** Contact your IT support team with this manual and any log files.

**Last Updated:** 12-Jul-2025