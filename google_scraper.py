import os
import pdfkit
import requests
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, build_from_document
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
import tkinter as tk
from tkinter import messagebox

# Define scopes for Gmail, Google Drive, and Google Photos APIs
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/drive.readonly',
          'https://www.googleapis.com/auth/photoslibrary.readonly']

CREDENTIALS_FILE = 'client_secret.json'
DISCOVERY_DOC_FILE = 'photoslibrary_v1.json'

def get_report_folder():
    base_path = os.path.dirname(os.path.abspath(__file__))
    report_folder = os.path.join(base_path, "Google Report")
    if not os.path.exists(report_folder):
        os.makedirs(report_folder)
    return report_folder

def authenticate_user(scopes):
    creds = None
    token_file = 'token.json'

    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, scopes)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, scopes)
            creds = flow.run_local_server(port=0)
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    return creds

def fetch_emails(service):
    query = 'category:primary'
    results = service.users().messages().list(userId='me', q=query).execute()
    messages = results.get('messages', [])

    email_data = []

    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id']).execute()

        headers = msg['payload']['headers']
        subject = next(header['value'] for header in headers if header['name'] == 'Subject')
        date = next(header['value'] for header in headers if header['name'] == 'Date')
        snippet = msg['snippet']

        email_data.append({
            'subject': subject,
            'date': date,
            'snippet': snippet
        })

    return email_data

def create_pdf(email_data):
    report_folder = get_report_folder()
    with open('gmail_template.html', 'r') as file:
        html_template = file.read()

    emails_html = ""
    for email in email_data:
        emails_html += f'''
        <div class="email-container">
            <h2 class="email-title">{email['subject']}</h2>
            <h4 class="email-date">{email['date']}</h4>
            <div class="email-snippet">{email['snippet']}</div>
        </div>
        '''

    final_html = html_template.replace('{{content}}', emails_html)
    pdf_path = os.path.join(report_folder, 'Gmail_Report.pdf')
    pdfkit.from_string(final_html, pdf_path)
    print(f"PDF report created: {pdf_path}")

def create_local_folder(folder_name):
    report_folder = get_report_folder()
    folder_path = os.path.join(report_folder, folder_name)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    return folder_path

def download_file_to_folder(file_id, folder_name, file_name, service):
    request = service.files().get_media(fileId=file_id)
    file_path = os.path.join(folder_name, file_name)
    with open(file_path, 'wb') as fh:
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}% of {file_name}. File saved to {file_path}")

def list_and_download_all_files(service):
    results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name, mimeType)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        folder_name = create_local_folder('Google Drive Data')
        for item in items:
            if item['mimeType'] != 'application/vnd.google-apps.folder':
                print(f'Downloading {item["name"]} ({item["id"]})')
                download_file_to_folder(item['id'], folder_name, item['name'], service)
            else:
                print(f'Skipping folder {item["name"]} ({item["id"]})')

def authenticate_google_photos(creds):
    if not os.path.exists(DISCOVERY_DOC_FILE):
        print(f"Error: Discovery document '{DISCOVERY_DOC_FILE}' not found.")
        return None

    try:
        with open(DISCOVERY_DOC_FILE, 'r') as f:
            discovery_doc = f.read()

        service = build_from_document(discovery_doc, credentials=creds)
        print("Google Photos service built successfully.")
        return service
    except HttpError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None
    except Exception as e:
        print(f"An error occurred during authentication or service creation: {e}")
        return None

def list_recent_photos(service, num_photos=10):
    try:
        results = service.mediaItems().list(pageSize=num_photos).execute()
        print("Recent photos retrieved successfully:")
        photos = results.get('mediaItems', [])
        
        if not photos:
            print("No photos found.")
            return []

        photo_data = []
        for photo in photos:
            photo_info = {
                "filename": photo['filename'],
                "id": photo['id'],
                "url": photo['baseUrl'],
                "mimeType": photo['mimeType']
            }
            print(f" - {photo_info['filename']} (ID: {photo_info['id']})")
            photo_data.append(photo_info)

        return photo_data
    except HttpError as http_err:
        print(f"HTTP error occurred when calling the API: {http_err}")
        return []
    except Exception as e:
        print(f"An error occurred while retrieving photos: {e}")
        return []

def download_photo(photo_info, folder_path):
    try:
        response = requests.get(photo_info['url'])
        if response.status_code == 200:
            filename = os.path.join(folder_path, photo_info['filename'])
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"Photo saved as '{filename}'")
        else:
            print(f"Failed to download photo '{photo_info['filename']}': {response.status_code}")
    except Exception as e:
        print(f"An error occurred while downloading photo '{photo_info['filename']}': {e}")

def main():
    # Authenticate and build services for Gmail, Google Drive, and Google Photos
    creds = authenticate_user(SCOPES)
    gmail_service = build('gmail', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    photos_service = authenticate_google_photos(creds)
    
    # Fetch and save Gmail data
    email_data = fetch_emails(gmail_service)
    create_pdf(email_data)
    
    # List and download Drive files
    list_and_download_all_files(drive_service)
    
    # List and download recent Google Photos
    photos_folder = create_local_folder("Google Photos Data")

    if photos_service is not None:
        recent_photos = list_recent_photos(photos_service, num_photos=10)
        if recent_photos:
            for photo in recent_photos:
                download_photo(photo, photos_folder)
    else:
        print("Failed to create the Google Photos service.")

    print("PDF report created, Drive files, and Photos downloaded successfully!")

    # Show success message and open the report folder
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    messagebox.showinfo("Success", "Google data extraction completed successfully!")
    os.startfile(get_report_folder())

if __name__ == '__main__':
    main()