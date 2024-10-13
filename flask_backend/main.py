from __future__ import print_function
import os
import google.auth
import re
import pypandoc
from docx import Document
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload


# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']

def authenticate():
    """Authenticate and return the service for Google Docs and Google Drive."""
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    
    # Delete token.json if it is invalid
    if os.path.exists('token.json'):
        try:
            creds = google.auth.load_credentials_from_file('token.json')[0]
        except google.auth.exceptions.DefaultCredentialsError:
            print("Invalid token.json file. Deleting it and starting the authentication process again.")
            os.remove('token.json')
            creds = None
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Create the Docs and Drive service
    docs_service = build('docs', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)
    return docs_service, drive_service


def share_image(drive_service, image_id):
    permission = {
        'type': 'anyone',
        'role': 'writer'
    }

    drive_service.permissions().create(
        fileId=image_id,
        body=permission,
        fields='id'
    ).execute()



def get_document_length(docs_service, document_id):
    """Fetches the current document content length."""
    doc = docs_service.documents().get(documentId=document_id).execute()
    content_length = sum(len(e.get('textRun', {}).get('content', '')) for e in doc.get('body', {}).get('content', []))
    return content_length

def create_google_doc(docs_service, drive_service, content1, content2, content3, image_path1, image_path2):
    try:
        # Create a new document
        document = docs_service.documents().create(body={'title': 'Generated Document'}).execute()
        
        # Get the document ID
        document_id = document['documentId']

        # Upload the first image to Google Drive
        file_metadata = {'name': image_path1, 'mimeType': 'image/jpeg'}
        media = MediaFileUpload(image_path1, mimetype='image/jpeg')
        image_file1 = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        image_id1 = image_file1.get('id')
        share_image(drive_service, image_id1)  # Share the image to make it accessible

        # Upload the second image to Google Drive
        file_metadata = {'name': image_path2, 'mimeType': 'image/jpeg'}
        media = MediaFileUpload(image_path2, mimetype='image/jpeg')
        image_file2 = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        image_id2 = image_file2.get('id')
        share_image(drive_service, image_id2)  # Share the image to make it accessible

        # Prepare the requests for inserting content and images
        requests = []

        # Insert content1
        requests.append({'insertText': {'location': {'index': 1}, 'text': content1 + '\n'}})

        # Execute the batchUpdate to insert content1
        docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

        # Get updated document length
        current_index = get_document_length(docs_service, document_id) + 1

        # Insert the first image after content1
        requests = [{
            'insertInlineImage': {
                'location': {'index': current_index},  # Ensure the image is inserted after content1
                'uri': f'https://drive.google.com/uc?id={image_id1}',
                'objectSize': {'height': {'magnitude': 300, 'unit': 'PT'}, 'width': {'magnitude': 300, 'unit': 'PT'}}
            }
        }]

        # Execute batchUpdate to insert first image
        docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

        # Get updated document length
        current_index = get_document_length(docs_service, document_id) + 1

        # Insert content2 after the first image
        requests = [{'insertText': {'location': {'index': current_index}, 'text': content2 + '\n'}}]

        # Execute batchUpdate to insert content2
        docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

        # Get updated document length
        current_index = get_document_length(docs_service, document_id) + 1

        # Insert the second image after content2
        requests = [{
            'insertInlineImage': {
                'location': {'index': current_index},
                'uri': f'https://drive.google.com/uc?id={image_id2}',
                'objectSize': {'height': {'magnitude': 300, 'unit': 'PT'}, 'width': {'magnitude': 300, 'unit': 'PT'}}
            }
        }]

        # Execute batchUpdate to insert second image
        docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

        # Get updated document length
        current_index = get_document_length(docs_service, document_id) + 1

        # Insert content3 after the second image
        requests = [{'insertText': {'location': {'index': current_index}, 'text': content3 + '\n'}}]

        # Execute batchUpdate to insert content3
        docs_service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()

        # Print the document link
        document_link = f'https://docs.google.com/document/d/{document_id}/edit'
        print(f'Document created: {document_link}\n')
        return document_id, document_link

    except HttpError as err:
        print(f'An error occurred while creating the document: {err}')
        return None, None



def share_google_doc(drive_service, doc_id, user_email):
    """Share the Google Doc with a specified email."""
    try:
        # Create a new permission
        permission = {
            'type': 'user',
            'role': 'writer',  # Can be 'reader' for read-only access
            'emailAddress': user_email
        }

        # Add the permission to the file
        drive_service.permissions().create(
            fileId=doc_id,
            body=permission,
            fields='id'
        ).execute()

        print(f'Document shared with {user_email}')
    except HttpError as error:
        print(f'An error occurred while sharing the document: {error}')


def convert_md_to_docx(md_file_path, docx_file_path):
    try:
        # Convert the Markdown file to DOCX
        pypandoc.convert_file(md_file_path, 'docx', outputfile=docx_file_path)
        # print(f"Successfully converted '{md_file_path}' to '{docx_file_path}'.")
    except Exception as e:
        print(f"An error occurred: {e}")


def read_docx(file_path):
    doc = Document(file_path)
    content = []
    
    for para in doc.paragraphs:
        if para.style.name.startswith('Heading'):
            content.append(f'\n{para.text.upper()}\n')  # Uppercase headings
        elif para.runs:
            formatted_text = ""
            for run in para.runs:
                # Check for bold and italic text
                if run.bold:
                    formatted_text += f'**{run.text}**'
                elif run.italic:
                    formatted_text += f'*{run.text}*'
                else:
                    formatted_text += run.text
            content.append(formatted_text)
        else:
            content.append(para.text)  # Normal text

    return '\n'.join(content)


def main():
    # Authenticate and get credentials
    docs_service, drive_service = authenticate()

    md_file = 'insights.md'  # Replace with your Markdown file path
    docx_file = 'insights.docx'  # Replace with your desired DOCX output file path
    convert_md_to_docx(md_file, docx_file)

    md_file = 'data.md'  # Replace with your Markdown file path
    docx_file = 'data.docx'  # Replace with your desired DOCX output file path
    convert_md_to_docx(md_file, docx_file)

    md_file = 'news.md'  # Replace with your Markdown file path
    docx_file = 'news.docx'  # Replace with your desired DOCX output file path
    convert_md_to_docx(md_file, docx_file)

    # Read content from the .docx files
    content1 = read_docx('insights.docx')
    content2 = read_docx('news.docx')
    content3 = read_docx('data.docx')

    # Path to the image
    image_path2 = 'industry_performance_graph.jpg'
    image_path1 = 'market_cap_distribution.jpg'

    # Create Google Doc and insert content
    document_id, document_link = create_google_doc(docs_service, drive_service, content1, content2, content3, image_path1, image_path2)

    # # Output the link to the document
    # if document_id:
    #     # Ask for email to share the document with
    #     user_email = input("Enter the email address to share the document with: ")

    #     # Share the document with the specified email
    #     share_google_doc(drive_service, document_id, user_email)

    #     print(f'You can view the document here: {document_link}')

if __name__ == '__main__':
    main()
