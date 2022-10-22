import imaplib
import os
import email
import smtplib
import subprocess
import time
from datetime import datetime
import pytz
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

email_user = "bchigh.cpc@gmail.com"
email_pass = "qrwvizsjumxddbvw"
pi = 3.141592


def check_solution(result, answer):  # configured for 10/24 problem
    lower = pi - answer
    upper = pi + answer
    try:
        if lower < float(result) < upper:
            return True
        else:
            message = 'Subject: {}\n\n{}'.format("CPC Weekly: Incorrect Solution",
                                                 f"Sorry, it looks like your solution was incorrect. The expected answer was: {lower} < [number] < {upper}, and your answer was: {float(result)}.")
            server.sendmail(email_user, original_sender, message)
    except ValueError:
        print("Output could not be converted to type float")
        message = 'Subject: {}\n\n{}'.format("CPC Weekly: Incorrect Solution",
                                             f"Sorry, it looks like your solution was incorrect. The expected answer was: {lower} < [number] < {upper}, and your answer was: {result}.")
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
            if extension == "py":  # testing configured for 10/24
                print(f'Filename: {fileName}')
                r1 = subprocess.run(f'python CPCDownloadedFiles/{fileName}', input='100', shell=True,
                                    capture_output=True, text=True).stdout
                print(f"Test 1: in=100. Result: {r1}")
                r2 = subprocess.run(f'python CPCDownloadedFiles/{fileName}', input='1000', shell=True,
                                    capture_output=True, text=True).stdout
                print(f"Test 2: in=1000. Result: {r2}")
                r3 = subprocess.run(f'python CPCDownloadedFiles/{fileName}', input='10000', shell=True,
                                    capture_output=True, text=True).stdout
                print(f"Test 3: in=10000. Result: {r3}")

                if check_solution(r1, 0.75) and check_solution(r2, 0.25) and check_solution(r3, 0.075):
                    print("Correct Solution!")
                    message = 'Subject: {}\n\n{}'.format(f"CPC Weekly: Correct Solution! {house} ",
                                                         "Congrats on the correct solution!")
                    server.sendmail(email_user, original_sender, message)  # to solver

                    # this section from https://www.tutorialspoint.com/send-mail-with-attachment-from-your-gmail-account-using-python
                    message = MIMEMultipart()
                    message['From'] = email_user
                    message['To'] = "56spc56@gmail.com"
                    message['Subject'] = "CPC Weekly: Correct Solution Detected"
                    mail_content = f"Correct solution from {original_sender} of {house}, please check the file"
                    message.attach(MIMEText(mail_content, 'plain'))

                    # mine
                    with open(f"CPCDownloadedFiles/{fileName}") as p:
                        lines = p.readlines()
                        with open(f'{fileName}.txt', 'w') as f:
                            f.writelines(lines)

                    # back to link author
                    attach_file_name = f'{fileName}.txt'
                    attach_file = open(attach_file_name, 'rb')  # Open the file as binary mode
                    payload = MIMEBase('application', 'octate-stream')
                    payload.set_payload(attach_file.read())
                    encoders.encode_base64(payload)  # encode the attachment
                    # add payload header with filename
                    payload.add_header('Content-Disposition', "attachment; filename= %s" % f'{fileName}.txt')
                    message.attach(payload)
                    text = message.as_string()
                    message = 'Subject: {}\n\n{}'.format(f"CPC Weekly: Correct Solution Detected",
                                                         f"Correct solution from {original_sender} of {house}")
                    server.sendmail(email_user, "56spc56@gmail.com", text)  # to me

            else:
                print("Invalid Filetype")

            server.quit()

    mail.close()
    mail.logout()
    time.sleep(600)
