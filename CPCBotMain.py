import imaplib
import os
import email
import smtplib
import subprocess
import time
from datetime import datetime
import pytz

email_user = "bchigh.cpc@gmail.com"
email_pass = "qrwvizsjumxddbvw"


def check_solution(result, answer):  # for testing
    try:
        if int(result) == answer:
            return True
        else:
            message = 'Subject: {}\n\n{}'.format("CPC Weekly: Incorrect Solution",
                                                 f"Sorry, it looks like your solution was incorrect. The expected answer was: {answer}, and your answer was: {int(result)}.")
            server.sendmail(email_user, original_sender, message)
    except ValueError:
        print("Output could not be converted to type int")
        message = 'Subject: {}\n\n{}'.format("CPC Weekly: Incorrect Solution",
                                             f"Sorry, it looks like your solution was incorrect. The expected answer was: {answer}, and your answer was: {result}.")
        server.sendmail(email_user, original_sender, message)


while True:
    mail = imaplib.IMAP4_SSL("imap.gmail.com", port=993)
    mail.login(email_user, email_pass)
    tz = pytz.timezone('US/Eastern')
    print("login success at", datetime.now(tz).strftime("%m/%d/%Y %H:%M:%S"))
    mail.select("INBOX")
    type, data = mail.search(None, 'ALL')
    typ, data = mail.fetch(str(len(data[0].split())), '(RFC822)')
    raw_email = data[0][1]
    raw_email_string = raw_email.decode('utf-8')
    email_message = email.message_from_string(raw_email_string)  # downloading attachments
    original_sender = email_message["From"]
    house = email_message["Subject"]
    for part in email_message.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        fileName = part.get_filename()
        if bool(fileName):
            filePath = os.path.join('CPCDownloadedFiles', fileName)
            if not os.path.isfile(filePath):
                fp = open(filePath, 'wb')
                fp.write(part.get_payload(decode=True))
                fp.close()
            print(f'Downloaded "{fileName}" from "{original_sender}"')

            global server
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(email_user, email_pass)
            SUBJECT = "Subject"
            TEXT = "Text"

            message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

            server.sendmail(email_user, email_user, message)

            extension = fileName.split(".")[1]
            if extension == "py":
                r1 = subprocess.run(['python.exe', 'testhello.py'], input='100', capture_output=True, text=True).stdout
                r2 = subprocess.run(['python.exe', 'testhello.py'], input='72', capture_output=True, text=True).stdout
                r3 = subprocess.run(['python.exe', 'testhello.py'], input='5274', capture_output=True, text=True).stdout

                if check_solution(r1, 49) and check_solution(r2, 35) and check_solution(r3, 2636):
                    message = 'Subject: {}\n\n{}'.format(f"CPC Weekly: Correct Solution Detected, {house} House",
                                                         "Please check your server files to verify the solution")
                    server.sendmail(email_user, "56spc56@gmail.com", message)
            else:
                print("Invalid Filetype")

            server.quit()

    mail.close()
    mail.logout()
    time.sleep(600)
