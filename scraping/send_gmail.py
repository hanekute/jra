import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
from email.mime.text import MIMEText
from apiclient import errors
 
 
# 1. Gmail APIのスコープを設定
SCOPES = ['https://www.googleapis.com/auth/gmail.send']
 
# 2. メール本文の作成
def create_message(sender, to, subject, message_text):
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    encode_message = base64.urlsafe_b64encode(message.as_bytes())
    return {'raw': encode_message.decode()}
 
# 3. メール送信の実行
def send_message(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
         
 
def send_gmail(path, json_file, message_text="終了しました"):
     
    # 5. アクセストークンの取得
    #jsonファイルの場所とファイル名
    json_file = path + json_file
    creds = None
     
    if os.path.exists(path + 'token.pickle'):
        with open(path+'token.pickle', 'rb') as token:
            creds = pickle.load(token)
     
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
         
        else:
            flow = InstalledAppFlow.from_client_secrets_file(json_file, SCOPES)
            creds = flow.run_local_server()
             
        with open(path+'token.pickle', 'wb') as token:
            pickle.dump(creds, token)
             
     
    service = build('gmail', 'v1', credentials=creds)
     
    # 6. メール本文の作成
    sender = 'hanedakeisuke265@g.ecc.u-tokyo.ac.jp'
    to = 'hanehaneac@gmail.com'
    subject = 'プログラム終了'
    message = create_message(sender, to, subject, message_text)
     
    # 7. Gmail APIを呼び出してメール送信
    send_message(service, 'me', message)