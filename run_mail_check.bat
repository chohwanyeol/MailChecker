@echo off
cd /d D:\RPA\MailChecker

python -m pip install --upgrade pip >nul 2>&1
python -m pip install imaplib2 pyyaml >nul 2>&1
start "" /min python main.py
