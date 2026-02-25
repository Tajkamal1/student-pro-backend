from datetime import datetime, timedelta, timezone
from database import tasks
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# =============================
# Gmail Credentials (Hardcoded)
# =============================
EMAIL_ADDRESS = "gfree2960@gmail.com"
EMAIL_PASSWORD = "rhqh tzpc zxkv oftv"  # Gmail App Password


# =============================
# Email Sender
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

                <table style="width:100%; margin-top:15px; border-collapse: collapse;">
                    <tr>
                        <td style="padding:8px; background:#007bff; color:white; font-weight:bold;">
                            Task Title
                        </td>
                        <td style="padding:8px; border:1px solid #ddd;">
                            {task_title}
                        </td>
                    </tr>
                    <tr>
                        <td style="padding:8px; background:#17a2b8; color:white; font-weight:bold;">
                            Due Date & Time
                        </td>
                        <td style="padding:8px; border:1px solid #ddd;">
                            {due}
                        </td>
                    </tr>
                </table>

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

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"[INFO] Email sent to {to_email}")

    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")


# =============================
# Task Checker (Called by FastAPI endpoint)
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

            due = datetime.fromisoformat(
                task["dueDateTime"]
            ).replace(tzinfo=ist)

            user_email = task.get("email")
            user_name = task.get("name")

            if user_email and user_name and now <= due <= (now + timedelta(hours=1)):

                send_email(
                    user_email,
                    f"Reminder: Task '{task['title']}' due soon",
                    task
                )

                tasks.update_one(
                    {"_id": task["_id"]},
                    {"$set": {"notified": True}}
                )

                print(f"[INFO] Task marked notified: {task['_id']}")

        except Exception as e:
            print(f"[ERROR] Checking task {task.get('_id')}: {e}")

    print("[INFO] Task checking completed.")