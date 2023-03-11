from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
import os
from email_data import from_, to_, message_text, subject_, file_to_send_
import schedule
from datetime import datetime
import time


creds = None

if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/gmail.compose'])
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', ['https://www.googleapis.com/auth/gmail.compose'])
        creds = flow.run_local_server(port=0)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())
service = build('gmail', 'v1', credentials=creds)


def create_message():    
    message = MIMEMultipart()
    message['to'] = to_
    message['subject'] = subject_
    message.attach(MIMEText(message_text, 'plain'))
    filename = file_to_send_
    attachment = open(filename, 'rb')
    part = MIMEBase('application', 'octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(part)
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return raw_message

def send_email(service, user_id, raw_message):
    global response
    now = datetime.now()    
    current_time = now.strftime("%H:%M")
    try:
        message = service.users().messages().send(
            userId=user_id,
            body={'raw': raw_message}).execute()
        response = "Message was sent successfully ", current_time
    except HttpError as error:
        response = (f'An error occurred: {error}'), current_time
    
    
def send_message_on_time(service_, user_id_, raw_message_):
    global response
    schedule.every().day.at("17:02").do(send_email, service=service_, user_id=user_id_, raw_message= raw_message_)
    while True:
        schedule.run_pending()   
        if response:
            print(f"Sending email with result: {response}")
            log_messages(response)
            response = None
        time.sleep(1)

def log_messages(log_data):
    log_message = ''
    for item in log_data:
        log_message += item   
    log_file = "C:\\Users\\PC\\Documents\\courses\\report\\sent_log.txt"
    file_handle = open(log_file, 'a+')
    file_handle.write(log_message + "\n")
    file_handle.close()

response = None
raw_message_ = create_message()
log_data = send_message_on_time(service, 'me', raw_message_)



