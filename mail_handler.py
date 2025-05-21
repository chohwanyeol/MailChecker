import imaplib
import email
import os
import yaml
from datetime import datetime, timezone
from email.header import decode_header
from email.utils import parseaddr, parsedate_to_datetime


# ------------------------------
# config.yaml 정보 가져오기
# ------------------------------
def load_config(path="config.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

config = load_config()
email_user = config["계정정보"]["메일계정"]
subject_keywords = config["필터"]["제목_키워드"]
# 메일 계정 정보
IMAP_SERVER = config["계정정보"]["서버"]
EMAIL_ACCOUNT = config["계정정보"]["메일계정"]
APP_PASSWORD = config["계정정보"]["앱패스워드"]

# ------------------------------
# last_checked.yaml 정보 
# ------------------------------
def load_last_checked(path="last_checked.yaml"):
    """last_checked.yaml이 없거나 비어있으면 1970년으로 처리"""
    if not os.path.exists(path):
        return datetime(1970, 1, 1, tzinfo=timezone.utc)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return parsedate_to_datetime(data.get("마지막확인시각")) or datetime(1970, 1, 1, tzinfo=timezone.utc)
    except Exception:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)

def save_last_checked(dt, path="last_checked.yaml"):
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump({"마지막확인시각": dt.strftime("%a, %d %b %Y %H:%M:%S %z")}, f, allow_unicode=True)

        

# ------------------------------
# 메일 서버 연결 및 로그인
# ------------------------------
def connect_to_mailbox():
    """메일 서버 연결 + 로그인 + 받은편지함 선택"""
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_ACCOUNT, APP_PASSWORD)
    mail.select("INBOX")
    return mail

# ------------------------------
# 최근 메일 ID 리스트 추출
# ------------------------------
def get_recent_mail_ids(mail, count=5):
    """메일 서버에서 최근 count개의 메일 ID 추출"""
    result, data = mail.search(None, "ALL")
    mail_ids = data[0].split()[-count:]  # 최신 메일 count개
    return mail_ids

# ------------------------------
# 메일 ID로 실제 메일 가져오기
# ------------------------------
def fetch_email_by_id(mail, mail_id):
    """단일 메일 ID를 이메일 객체로 변환"""
    result, message_data = mail.fetch(mail_id, "(RFC822)")
    raw_email = message_data[0][1]
    return email.message_from_bytes(raw_email)

# ------------------------------
# 최근 메일 N개 가져오기 (통합)
# ------------------------------
def fetch_recent_emails(count=5):
    """최근 N개의 이메일 객체 리스트 반환"""
    mail = connect_to_mailbox()
    mail_ids = get_recent_mail_ids(mail, count)

    messages = []
    for mail_id in mail_ids:
        msg = fetch_email_by_id(mail, mail_id)
        messages.append(msg)

    mail.logout()
    return messages

# ------------------------------
# 개별 메일 정보 파싱 함수들
# ------------------------------
def get_subject(msg):
    """메일 제목 추출 및 디코딩"""
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
        subject = subject.decode(encoding if encoding else 'utf-8')
    return subject

def get_sender(msg):
    """보낸 사람 정보 추출"""
    name, email_address = parseaddr(msg.get("From"))
    return email_address

def get_body(msg):
    """텍스트 본문 추출 (text/plain)"""
    for part in msg.walk():
        if part.get_content_type() == "text/plain" and part.get('Content-Disposition') is None:
            body = part.get_payload(decode=True)
            charset = part.get_content_charset() or 'utf-8'
            return body.decode(charset, errors="replace")
    return "(본문 없음)"

def save_attachments(msg, save_path="./downloads"):
    """메일 객체에서 첨부파일을 저장"""
    saved_files = []

    for part in msg.walk():
        content_disposition = str(part.get("Content-Disposition"))

        # 첨부파일인지 확인
        if "attachment" in content_disposition:
            filename = part.get_filename()

            # 파일명이 인코딩된 경우 디코딩
            if filename:
                decoded_name, enc = decode_header(filename)[0]
                if isinstance(decoded_name, bytes):
                    filename = decoded_name.decode(enc or 'utf-8')

                # 저장 경로 생성
                os.makedirs(save_path, exist_ok=True)
                file_path = os.path.join(save_path, filename)

                # 파일 저장
                with open(file_path, "wb") as f:
                    f.write(part.get_payload(decode=True))

                saved_files.append(file_path)

    if saved_files:
        return saved_files
    else:
        return ["(첨부파일 없음)"]

    
def get_mail_datetime(msg):
    """메일 수신 시각 (datetime 객체로 변환)"""
    date_str = msg.get("Date")
    try:
        return parsedate_to_datetime(date_str)
    except Exception:
        return None
    
# ------------------------------
# 메일 필터링
# ------------------------------
def is_target_email(msg, config):
    subject = get_subject(msg)
    sender = get_sender(msg)

    filters = config.get("필터", {})

    if "제목_키워드" in filters:
        if not any(kw in subject for kw in filters["제목_키워드"]):
            return False

    if "허용_발신자" in filters:
        if not any(allowed in sender for allowed in filters["허용_발신자"]):
            return False

    return True

# ------------------------------
# 전체 메일 파싱 및 출력
# ------------------------------
def parse_email(msg):
    """메일 객체 1개를 사람이 읽을 수 있게 출력"""
    subject = get_subject(msg)
    sender = get_sender(msg)
    body = get_body(msg)

    print(f"📧 제목: {subject}")
    print(f"👤 발신자: {sender}")
    print("📨 본문 내용:")
    print(body)
    print("-" * 40)

# ------------------------------
# 전체 메일 조건에 맞게 필터링
# ------------------------------
def filter_email():
    """툭정 메일 객체 필터"""
    last_checked = load_last_checked()
    filtered_message = []
    messages = fetch_recent_emails(10)
    
    for msg in messages:
        mail_dt = get_mail_datetime(msg)
        if last_checked and mail_dt and mail_dt <= last_checked:
            continue  # 이전에 본 메일이면 건너뜀
        
        result = is_target_email(msg, config)
        if result:
            filtered_message.append(msg)

    # 가장 최근 메일의 시간으로 업데이트
    if messages:
        latest_dt = max((get_mail_datetime(m) for m in messages if get_mail_datetime(m)), default=None)
        if latest_dt:
            save_last_checked(latest_dt)
            
    return filtered_message
    

# ------------------------------
# 단독 실행용 테스트
# ------------------------------
if __name__ == "__main__":
    print("📥 최근 메일 확인 중...\n")
    messages = fetch_recent_emails(3)
    for msg in messages:
        parse_email(msg)
