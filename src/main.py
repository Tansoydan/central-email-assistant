import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def authenticate_gmail():
    
    creds = None

    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:

            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json','w') as token:
            token.write(creds.to_json())
    
    service = build('gmail', 'v1', credentials = creds)
    return service

def fetch_unread_emails(service, max_results = 5):
        
    results = service.users().messages().list(
        userId='me',
        q='is:unread',
        maxResults=max_results
    ).execute()
    
    messages = results.get('messages', [])
    
    if not messages:
        print("No unread emails found!")
        return []
    
    print(f"Found {len(messages)} unread email(s)\n")
    
   
    emails = []
    for msg in messages:
        
        message = service.users().messages().get(
            userId='me',
            id=msg['id'],
            format='full'
        ).execute()
        
        
        headers = message['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        
        
        snippet = message.get('snippet', '')
        
        email_data = {
            'id': msg['id'],
            'subject': subject,
            'from': sender,
            'snippet': snippet
        }
        emails.append(email_data)
        
        print(f"   Subject: {subject}")
        print(f"   From: {sender}")
        print(f"   Preview: {snippet[:100]}...")
        print("-" * 80)
    
    return emails


if __name__ == "__main__":
    gmail_service = authenticate_gmail()
    print("Connected to Gmail\n")

    emails = fetch_unread_emails(gmail_service, max_results= 5)

    print(f"\n Done! Found {len(emails)} unread emails")

    