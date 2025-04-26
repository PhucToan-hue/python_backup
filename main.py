# Các thư viện cần thiết
import os
import smtplib
import shutil
import schedule
import time
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv


load_dotenv()


EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

def send_email(subject, body):
    try:
        message = MIMEMultipart()
        message['From'] = EMAIL_USER
        message['To'] = EMAIL_RECEIVER
        message['Subject'] = subject
        message.attach(MIMEText(body, 'plain'))
        # Kết nối tới server
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Bắt đầu mã hóa TLS
        server.login(EMAIL_USER, EMAIL_PASS)
        # Gửi
        server.send_message(message)
        server.quit()
    except Exception as e:
        print(f"Lỗi khi gửi email: {e}")


# backup database
def backup_database():
    source_folder = 'database'
    backup_folder = 'backup'
    # Lấy thời gian hiện tại đặt tên file backup
    time_now = datetime.now().strftime('%Y%m%d_%H%M%S')
    # Danh sách file backup
    success_files = []
    failed_files = []
    # Nếu thư mục backup chưa tồn tại, tự động tạo mới
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)
    # Duyệt qua các file trong database
    for file_name in os.listdir(source_folder):
        if file_name.endswith('.sql') or file_name.endswith('.sqlite3'):
            # Đường dẫn file gốc và file backup
            source_path = os.path.join(source_folder, file_name)
            backup_file_name = f"{file_name}_{time_now}"
            backup_path = os.path.join(backup_folder, backup_file_name)
            try:
                # Copy file sang thư mục backup
                shutil.copy2(source_path, backup_path)
                success_files.append(file_name)
            except Exception as e:
                # Nếu lỗi thì lưu lại
                failed_files.append(f"{file_name}: {e}")
    return success_files, failed_files

def backup_job():
    # Thực hiện backup
    success_files, failed_files = backup_database()
    # Lấy thời gian hiện tại để ghi vào email
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Nếu có file backup thành công
    if success_files:
        subject = "Backup thành công"
        body = f"Các file đã backup: {', '.join(success_files)} vào lúc {current_time}."
    else:
        subject = "Backup thất bại"
        body = f"Không backup được file nào. Các lỗi: {', '.join(failed_files)} vào lúc {current_time}."
    # Gửi email báo cáo
    send_email(subject, body)
    print(f"Đã thực hiện backup lúc {current_time}")


# lên lịch chạy
def main():
    # Đặt lịch 
    schedule.every().day.at("00:00").do(backup_job)
    print("Đã cài đặt lịch backup. Chương trình đang chờ đến giờ...")
    while True:
        schedule.run_pending()  
        time.sleep(60)  

if __name__ == '__main__':
    main()
