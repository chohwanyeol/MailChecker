Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "D:\RPA\MailChecker\run_mail_check.bat" & Chr(34), 0
Set WshShell = Nothing
