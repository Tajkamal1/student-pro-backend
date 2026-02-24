from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta, timezone
from database import tasks
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

EMAIL_ADDRESS = "gfree2960@gmail.com"
EMAIL_PASSWORD = "rhqh tzpc zxkv oftv"  # Gmail App Password

# -----------------------------
# Email Sender with HTML formatting
# -----------------------------
def send_email(to_email, subject, task):
    try:
        user_name = task.get("name", "User")
        task_title = task.get("title", "Task")
        due = datetime.fromisoformat(task["dueDateTime"]).strftime("%Y-%m-%d %H:%M")

        # HTML Email Content
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f8f9fa; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background-color: #ffffff; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); padding: 20px;">
                <h2 style="color: #007bff;">Task Reminder</h2>
                <p>Hi <strong style="color: #28a745;">{user_name}</strong>,</p>
                <p>This is a friendly reminder for your upcoming task:</p>

                <table style="width: 100%; border-collapse: collapse; margin-top: 15px;">
                    <tr>
                        <td style="padding: 8px; font-weight: bold; color: #ffffff; background-color: #007bff;">Task Title</td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{task_title}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; font-weight: bold; color: #ffffff; background-color: #17a2b8;">Due Date & Time</td>
                        <td style="padding: 8px; border: 1px solid #dee2e6;">{due}</td>
                    </tr>
                </table>

                <p style="margin-top: 20px; color: #6c757d;">- Sent by <strong>Student Pro</strong></p>
            </div>
        </body>
        </html>
        """

        msg = MIMEMultipart("alternative")
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(html_content, 'html'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"[INFO] Email sent to {to_email}")

    except Exception as e:
        print(f"[ERROR] Failed to send email to {to_email}: {e}")

# -----------------------------
# Task Checker
# -----------------------------
def check_tasks():
    ist = timezone(timedelta(hours=5, minutes=30))  # India timezone
    now = datetime.now(ist)

    tasks_cursor = tasks.find({
        "completed": False,
        "notified": {"$ne": True}  # Only send if not already notified
    })

    for task in tasks_cursor:
        try:
            due = datetime.fromisoformat(task["dueDateTime"]).replace(tzinfo=ist)
            user_email = task.get("email")
            user_name = task.get("name")

            # Send email if task is within 1 hour before deadline
            if user_email and user_name and now <= due <= (now + timedelta(hours=1)):
                send_email(
                    user_email,
                    f"Reminder: Task '{task['title']}' due soon",
                    task  # pass the task dictionary
                )
                # Mark task as notified
                tasks.update_one({"_id": task["_id"]}, {"$set": {"notified": True}})

        except Exception as e:
            print(f"[ERROR] Checking task {task.get('_id')}: {e}")

# -----------------------------
# Scheduler Starter
# -----------------------------
def start_scheduler():
    scheduler = BackgroundScheduler(timezone=timezone.utc)
    scheduler.add_job(check_tasks, 'interval', minutes=1, next_run_time=datetime.now(timezone.utc))
    scheduler.start()
    print("[INFO] Task notification scheduler started...")

# -----------------------------
# Start the scheduler when this script runs
# -----------------------------
if __name__ == "__main__":
    start_scheduler()