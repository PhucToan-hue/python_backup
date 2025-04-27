import os
import smtplib
import shutil
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv
import schedule


load_dotenv()

SENDER_EMAIL = os.getenv("EMAIL_USER")
SENDER_PASSWORD = os.getenv("EMAIL_PASS")
RECEIVER_EMAIL = os.getenv("EMAIL_RECEIVER")

def get_current_timestamp():
    return datetime.now().strftime('%Y%m%d_%H%M%S')

def create_backup_directory(path):
    os.makedirs(path, exist_ok=True)

def list_database_files(directory, extensions=('.sql', '.sqlite3')):
    return [f for f in os.listdir(directory) if f.endswith(extensions)]

def copy_files(files, source, destination):
    success = []
    failure = []
    for file in files:
        src_path = os.path.join(source, file)
        dest_file = f"{file}_{get_current_timestamp()}"
        dest_path = os.path.join(destination, dest_file)
        try:
            shutil.copy2(src_path, dest_path)
            success.append(file)
        except Exception as e:
            failure.append(f"{file} -> {e}")
    return success, failure

def compose_email(subject, message):
    email = MIMEMultipart()
    email['From'] = SENDER_EMAIL
    email['To'] = RECEIVER_EMAIL
    email['Subject'] = subject
    email.attach(MIMEText(message, 'plain'))
    return email

def send_email(subject, content):
    try:
        email_message = compose_email(subject, content)
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(email_message)
    except Exception as e:
        print(f"Không thể gửi email: {e}")

def perform_backup():
    source_dir = 'database'
    backup_dir = 'backupdata'
    create_backup_directory(backup_dir)
    db_files = list_database_files(source_dir)
    successful, failed = copy_files(db_files, source_dir, backup_dir)
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if successful:
        subject = "Backup thành công"
        message = f"Sao lưu thành công các tệp: {', '.join(successful)} vào lúc {now}."
    else:
        subject = "Backup thất bại"
        message = f"Không sao lưu được tệp nào. Lỗi: {', '.join(failed)} vào lúc {now}."
    send_email(subject, message)
    print(f"[{now}] Đã hoàn tất quá trình backup.")

def start_scheduler():
    schedule.every().day.at("00:00").do(perform_backup)
    print(" Lịch trình backup đã được thiết lập. Đang chờ đến giờ...")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    start_scheduler()
