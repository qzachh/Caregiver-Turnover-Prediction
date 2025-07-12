import os
import smtplib
import ssl
import unicodedata
# --- NEW IMPORTS for attachments and HTML content ---
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# A concise, non-debugging version of the cleaning function
def _bulletproof_clean(text):
    """
    Normalizes and cleans a string to ensure it's simple ASCII,
    removing extra whitespace.
    """
    # Normalize unicode characters to their basic form
    normalized = unicodedata.normalize('NFKD', str(text))
    # Encode to ASCII, ignoring characters that can't be converted
    cleaned_bytes = normalized.encode('ascii', 'ignore')
    # Decode back to a string and strip leading/trailing whitespace
    return cleaned_bytes.decode('ascii').strip()

# ✅ REQUIREMENT #2: Template updated to use HTML for formatting
HTML_TEMPLATE = """
<html>
<body>
    <p><b>🚨 High & Medium Churn Risk Detected</b></p>
    <p><b>{n} caregivers</b> have a high or medium churn risk.<br>
    Top 5 highest risk potentials listed below:</p>
    <pre style="font-family: monospace; font-size: 14px;">{table}</pre>
    <p>The full and filtered prediction reports are attached to this email.</p>
</body>
</html>
"""

def _top_table(df):
    """Formats the top 5 high-risk caregivers into a string table."""
    rows = [
        f"- {r.caregiver_id}: {r.churn_probability:.2f}% ({r.days_to_quit_est} days left)"
        for _, r in df.nlargest(5, "churn_probability").iterrows()
    ]
    return "\n".join(rows)

def send_alerts(pred_df, full_report_path, filtered_report_path):
    """Filters for high and medium risk, and sends an HTML email with attachments."""
    relevant_risk_df = pred_df[pred_df['risk_level'].isin(['HIGH', 'MEDIUM'])]
    if relevant_risk_df.empty:
        print("No high or medium risk caregivers to report.")
        return

    # --- e-mail ---
    try:
        # 1. Fetch and CLEAN all variables from the environment
        smtp_host_raw = os.getenv("SMTP_HOST")
        assert smtp_host_raw is not None, "FATAL: SMTP_HOST environment variable not set."
        smtp_host = _bulletproof_clean(smtp_host_raw)

        smtp_port_str = os.getenv("SMTP_PORT")
        assert smtp_port_str is not None, "FATAL: SMTP_PORT environment variable not set."

        smtp_user = os.getenv("SMTP_USER")
        assert smtp_user is not None, "FATAL: SMTP_USER environment variable not set."

        smtp_pass_raw = os.getenv("SMTP_PASS")
        assert smtp_pass_raw is not None, "FATAL: SMTP_PASS environment variable not set."
        smtp_pass = _bulletproof_clean(smtp_pass_raw)

        alert_to = os.getenv("ALERT_TO")
        assert alert_to is not None, "FATAL: ALERT_TO environment variable not set."

        # 2. ✅ Create a multipart message object
        from_addr = _bulletproof_clean(smtp_user)
        to_addr = _bulletproof_clean(alert_to)
        
        msg = MIMEMultipart()
        msg['Subject'] = "[WeCare247] High & Medium churn risk caregivers"
        msg['From'] = from_addr
        msg['To'] = to_addr

        # 3. ✅ Prepare and attach the HTML body
        table = _top_table(relevant_risk_df)
        html_body = HTML_TEMPLATE.format(
            n=len(relevant_risk_df),
            table=table
        )
        msg.attach(MIMEText(html_body, 'html'))

        # 4. ✅ REQUIREMENT #1: Attach the report files
        for file_path in [full_report_path, filtered_report_path]:
            try:
                with open(file_path, "rb") as f:
                    # Create an application MIME object for the CSV
                    part = MIMEApplication(f.read(), Name=os.path.basename(file_path))
                # Add header to make it an attachment
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
                msg.attach(part)
                print(f"📎 Attached {os.path.basename(file_path)}")
            except FileNotFoundError:
                print(f"❌ Attachment Error: Could not find file {file_path}")
            except Exception as e:
                print(f"❌ Attachment Error: Failed to attach {file_path}. Reason: {e}")

        # 5. Send the email
        ctx = ssl.create_default_context()
        with smtplib.SMTP(smtp_host, int(smtp_port_str)) as s:
            s.starttls(context=ctx)
            s.login(smtp_user, smtp_pass)
            # Send the message as a string
            s.sendmail(from_addr, [to_addr], msg.as_string())

        print("📧 Email alert with attachments sent successfully.")

    except (AssertionError, Exception) as e:
        print(f"❌ Failed to send email alert: {e}")