from datetime import datetime, timedelta, timezone
from database import tasks
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os


# =============================
# ENV VARIABLES (SET IN RENDER)
# =============================
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


# =============================
# EMAIL SENDER FUNCTION
# =============================
def send_email(to_email, subject, task):
    try:
        user_name = task.get("name", "User")
        task_title = task.get("title", "Task")

        due = datetime.fromisoformat(
            task["dueDateTime"]
        ).strftime("%Y-%m-%d %H:%M")

        html_content = f"""
        <html>
        <body style="font-family: Arial; background-color: #f8f9fa; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: white;
                        border-radius: 10px; padding: 20px;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);">

                <h2 style="color: #007bff;">Task Reminder</h2>

                <p>Hi <strong style="color: #28a745;">{user_name}</strong>,</p>
                <p>Your task is due soon:</p>

                <p><strong>Task:</strong> {task_title}</p>
                <p><strong>Due:</strong> {due}</p>

                <p style="margin-top:20px; color:#6c757d;">
                    - Sent by Student Pro 🚀
                </p>

            </div>
        </body>
        </html>
        """

        msg = MIMEMultipart("alternative")
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(html_content, "html"))

        server = smtplib.SMTP("smtp.gmail.com", 587, timeout=15)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"[INFO] Email sent to {to_email}")
        return True

    except Exception as e:
        print(f"[ERROR] Email failed: {e}")
        return False


# =============================
# TASK CHECKER (CRON CALLS THIS)
# =============================
def check_tasks():
    print("[INFO] Checking tasks...")

    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)

    tasks_cursor = tasks.find({
        "completed": False,
        "notified": {"$ne": True}
    })

    for task in tasks_cursor:
        try:
            if not task.get("dueDateTime"):
                continue

            # Convert stored time to IST timezone
            due = datetime.fromisoformat(
                task["dueDateTime"]
            ).replace(tzinfo=ist)

            user_email = task.get("email")
            user_name = task.get("name")

            # Calculate time difference in seconds
            time_diff = (due - now).total_seconds()

            print("NOW:", now)
            print("DUE:", due)
            print("TIME DIFF (seconds):", time_diff)

            # Send reminder if due within next 65 minutes
            if user_email and user_name and 0 <= time_diff <= 3900:

                email_sent = send_email(
                    user_email,
                    f"Reminder: Task '{task['title']}' due soon",
                    task
                )

                if email_sent:
                    tasks.update_one(
                        {"_id": task["_id"]},
                        {"$set": {"notified": True}}
                    )
                    print(f"[INFO] Task marked notified: {task['_id']}")
                else:
                    print("[WARNING] Email not sent. Task not marked notified.")

        except Exception as e:
            print(f"[ERROR] Checking task {task.get('_id')}: {e}")

    print("[INFO] Task checking completed.")