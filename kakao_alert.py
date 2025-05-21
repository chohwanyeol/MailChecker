import tkinter as tk
from tkinter import messagebox

def send_alert(subject, sender):
    message = f"📩 새 메일\n제목: {subject}\n보낸이: {sender}"
    root = tk.Tk()
    root.withdraw()
    messagebox.showinfo("메일 알림", message)
    root.destroy()

def send_kakao_alert(subject, sender):
    """카카오톡 출력 시뮬레이션 (콘솔 출력)"""
    print("[카카오톡 알림]")
    print(f"제목: {subject}")
    print(f"발신: {sender}")
    print("-" * 40)

if __name__ == "__main__":
    send_alert("조환열", "drcho9709@naver.com")
