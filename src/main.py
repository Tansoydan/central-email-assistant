import os
import ollama
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


def analyze_email_with_ollama(email_data, model='phi3:mini'):

    print(f"\n Sending email to Ollama (model: {model})...\n")
    
    prompt = f"""You are a helpful email assistant for a property management company.

Email Subject: {email_data['subject']}
From: {email_data['from']}
Content: {email_data['snippet']}

Please provide:
1. A brief summary of this email
2. The main intent or request
3. Suggested category (inquiry, maintenance request, complaint, general)
"""
    
    try:
        # Send to Ollama
        response = ollama.chat(
            model=model,
            messages=[{
                'role': 'user',
                'content': prompt
            }]
        )
        
        result = response['message']['content']
        print("Ollama Response:")
        print("-" * 80)
        print(result)
        print("-" * 80)
        
        return result
        
    except Exception as e:
        print(f"Error connecting to Ollama: {e}")
        print("Make sure Ollama is running (try 'ollama serve' in another terminal)")
        return None


if __name__ == "__main__":
    print("Starting LENAH Assistant...\n")
    

    gmail_service = authenticate_gmail()
    print("Connected to Gmail!\n")
    
    
    emails = fetch_unread_emails(gmail_service, max_results=5)
    
    if emails:
        print(f"\n Found {len(emails)} unread email(s)")
        
        
        print("\n" + "="*80)
        print("TESTING OLLAMA WITH FIRST EMAIL")
        print("="*80)
        
        analyze_email_with_ollama(emails[0])
    else:
        print("\n No unread emails to analyze")