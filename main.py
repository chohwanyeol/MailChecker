from mail_handler import filter_email, get_subject, get_sender
from kakao_alert import send_alert





if __name__ == "__main__":
    print("📥 최근 메일 확인 중...\n")
    messages = filter_email()
    for msg in messages:
        subject = get_subject(msg)
        sender = get_sender(msg)
        send_alert(subject, sender)
