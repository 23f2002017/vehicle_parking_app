import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText 

HOST = "localhost"
PORT = 1025
SENDER = "park@ease.co.in" 
PASSWORD = ""
 

def send_email(to, subject, body):
    msg = MIMEMultipart()
    msg['From'] = SENDER
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    mail_server = smtplib.SMTP(HOST, PORT)
    mail_server.login(SENDER, PASSWORD)
    mail_server.send_message(msg)
    mail_server.quit()
    return True   
