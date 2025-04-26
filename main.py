import os
import smtplib
import shutil
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")


def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_RECEIVER
    msg['Subject'] = subject
    # Gắn nội dung
    msg.attach(MIMEText(body, 'plain'))
    # Kết nối server SMTP của Gmail
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    # Gửi email
    server.send_message(msg)
    server.quit()


def backup_database():
    # Thư mục chứa file cần backup
    source_folder = 'database'
    # Thư mục lưu file backup
    backup_folder = 'backup'
    # Thời gian hiện tại để thêm vào tên file backup
    time_now = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Danh sách file thành công và thất bại
    success_files = []
    failed_files = []

    # Duyệt từng file trong thư mục nguồn
    for file_name in os.listdir(source_folder):
        if file_name.endswith('.sql') or file_name.endswith('.sqlite3'):
            source_path = os.path.join(source_folder, file_name)
            new_file_name = file_name + '_' + time_now
            backup_path = os.path.join(backup_folder, new_file_name)

            try:
                shutil.copy2(source_path, backup_path)
                success_files.append(file_name)
            except Exception as e:
                failed_files.append(file_name + ': ' + str(e))

    return success_files, failed_files


def main():
    # Thực hiện backup
    success, failed = backup_database()
    # Lấy thời gian hiện tại để ghi vào email
    time_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Nếu có file thì sao lưu thành công
    if len(success) > 0:
        subject = 'Backup thành công'
        body = 'Đã backup thành công các file: ' + ', '.join(success) + ' vào lúc ' + time_now
    else:
        subject = 'Backup thất bại'
        body = 'Không backup được file nào. Các lỗi: ' + ', '.join(failed) + ' lúc ' + time_now

    # Gửi email thông báo
    send_email(subject, body)

# Chạy 
if __name__ == '__main__':
    main()
