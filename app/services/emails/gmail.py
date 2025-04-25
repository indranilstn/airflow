import os
import base64
from itertools import groupby

# from pprint import pprint
from typing import Generator, Any

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.emails.base_email import EmailService

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
ACCOUNT_FILE = os.environ['GOOGLE_APPLICATION_CREDENTIALS']

class Gmail(EmailService):
    """Google Gmail Service"""

    __slots__ = '__service'

    def authenticate(self, user_email) -> bool:
        """Authenticate using a service account and return the Gmail API service instance."""

        creds = service_account.Credentials.from_service_account_file(
            ACCOUNT_FILE,
            scopes=SCOPES
        ) if os.path.exists(ACCOUNT_FILE) else None

        # Delegate access to the desired user and build the service
        delegated_creds = creds.with_subject(user_email) if creds else None
        self.__service = build("gmail", "v1", credentials=delegated_creds) if delegated_creds else None

        return bool(self.__service)

    @staticmethod
    def decode(data):
        """Decode base64 URL-safe encoded content."""
        return base64.urlsafe_b64decode(data.encode("ASCII")).decode("utf-8", errors="ignore")

    def save_attachment(self, msg_id, part) -> None:
        """Download and save an attachment."""

        attachment_id = part['body']['attachmentId']
        attachment = self.__service.users().messages().attachments().get(
            userId="me", messageId=msg_id, id=attachment_id
        ).execute()

        data = base64.urlsafe_b64decode(attachment['data']) # noqa
        file_name = part['filename']
        # file_path = os.path.join(ATTACHMENTS_DIR, file_name)
        # with open(file_path, "wb") as f:
        #     f.write(data)

        print(f"Attachment: {file_name}")

    @classmethod
    def extract_email_body(cls, payload) -> Generator[tuple[str, Any], None, None]:
        """Extracts the email body (HTML or plain text)."""

        if "parts" in payload:
            for part in payload['parts']:
                mime_type = part['mimeType']
                if mime_type in ("text/plain", "text/html") and "data" in part['body']:
                    yield ("body", {'type': mime_type, 'data': cls.decode(part['body']['data'])})

                elif "attachmentId" in part['body']:  # Handle attachments
                    yield ("attachment", part)

                elif "parts" in part:
                    yield from cls.extract_email_body(part)

        elif "body" in payload and "data" in payload['body']:
            mime_type = payload['mimeType'] if "mimeType" in payload else "text/plain"
            yield ("body", {'type': mime_type, 'data': Gmail.decode(payload['body']['data'])})

        else:
            return

    def get_emails(self, max_results=5) -> Generator[tuple[dict, list], None, None]:
        """Fetch and process emails."""

        results = self.__service.users().messages().list(userId='me', maxResults=max_results).execute()
        messages = results.get("messages", [])

        for msg in messages:
            msg_data = self.__service.users().messages().get(userId="me", id=msg['id']).execute()
            headers = {header["name"]: header["value"] for header in msg_data['payload']['headers']}
            # subject = next((header['value'] for header in headers if header['name'] == "Subject"), "No Subject")
            # sender = next((header['value'] for header in headers if header['name'] == "From"), "Unknown Sender")

            body_list = []
            for content_type, content in self.extract_email_body(msg_data['payload']):
                if content_type == "body":
                    body_list.append(content)
                elif content_type == "attachment":
                    self.save_attachment(msg['id'], content)

            def key_fn(x: dict): return x["type"]
            body = {key: [item["data"] for item in group] for key, group in groupby(sorted(body_list, key=key_fn), key=key_fn)}

            yield headers, body

def test():
    """ Shows basic usage of the Gmail API.
        Lists the user's mails.
    """
    service = Gmail()
    try:
        USER_EMAIL = 'indranil@softechnation.com'
        service.get_emails() if service.authenticate(USER_EMAIL) else None

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f"An error occurred: {error}")
