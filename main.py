# main.py
import os
import smtplib
import shutil
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()  # đọc .env

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")


def send_email(subject, body):
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_USER
        msg['To'] = EMAIL_RECEIVER
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Error sending email: {e}")


def backup_database():
    src_folder = 'database'
    dest_folder = 'backup'
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    success = []
    failed = []

    for filename in os.listdir(src_folder):
        if filename.endswith('.sql') or filename.endswith('.sqlite3'):
            src_path = os.path.join(src_folder, filename)
            dest_path = os.path.join(dest_folder, f"{filename}_{timestamp}")
            try:
                shutil.copy2(src_path, dest_path)
                success.append(filename)
            except Exception as e:
                failed.append(f"{filename}: {str(e)}")

    return success, failed



def main():
    success, failed = backup_database()
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    if success:
        subject = "✅ Backup database thành công"
        body = f"Sao lưu thành công các file: {', '.join(success)} vào lúc {now}"
    else:
        subject = "❌ Backup database thất bại"
        body = f"Không thể sao lưu file nào. Lỗi: {', '.join(failed)} lúc {now}"

    send_email(subject, body)

if __name__ == "__main__":
    main()
