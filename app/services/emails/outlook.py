# import os
import requests

import msal
from .base_email import EmailService

# Microsoft Entra ID (Azure AD) credentials
CLIENT_ID = "your_client_id"
CLIENT_SECRET = "your_client_secret"
TENANT_ID = "your_tenant_id"

# Microsoft Graph API endpoints
AUTHORITY_URL = f"https://login.microsoftonline.com/{TENANT_ID}"
GRAPH_API_URL = "https://graph.microsoft.com/v1.0/me/messages"

# Scope for Microsoft Graph API
SCOPES = ["https://graph.microsoft.com/.default"]

class Outlook(EmailService):
    """Microsoft outlook email service"""

    __slots__ = "__token"

    def authenticate(self) -> bool:
        """Get an access token using client credentials"""

        app = msal.ConfidentialClientApplication(CLIENT_ID, authority=AUTHORITY_URL, client_credential=CLIENT_SECRET)
        token_response = app.acquire_token_for_client(scopes=SCOPES)

        if "access_token" in token_response:
            self.__token = token_response['access_token']
            return True
        else:
            print(f"Could not obtain access token: {token_response}")
            return False

    def get_emails(self, max_results=5):
        """Fetch emails and check for attachments"""

        access_token = self.__token
        headers = {"Authorization": f"Bearer {access_token}"}
        params = {"$top": max_results, "$select": "id,subject,from,receivedDateTime,body,hasAttachments"}

        response = requests.get(GRAPH_API_URL, params, headers=headers)
        if response.status_code == 200:
            emails = response.json().get("value", [])
            for email in emails:
                email_id = email['id']
                subject = email.get("subject", "No Subject")
                sender = email.get("from", {}).get("emailAddress", {}).get("address", "Unknown Sender")
                received = email.get("receivedDateTime", "Unknown Date")
                body_content = email.get("body", {}).get("content", "No Content Available")
                has_attachments = email.get("hasAttachments", False)

                print("="*50)
                print(f"Subject: {subject}")
                print(f"From: {sender}")
                print(f"Received: {received}")
                print(f"Body:\n{body_content}\n")

                if has_attachments:
                    print("Attachments found! Downloading...\n")
                    self.save_attachment(email_id)
        else:
            print(f"Error fetching emails: {response.status_code} - {response.text}")

    def save_attachment(self, msg_id) -> None:
        """Download and save attachments from an email"""

        access_token = self.__token
        attachments_url = f"https://graph.microsoft.com/v1.0/me/messages/{msg_id}/attachments"
        headers = {"Authorization": f"Bearer {access_token}"}

        response = requests.get(attachments_url, headers=headers)
        if response.status_code == 200:
            attachments = response.json().get("value", [])
            for attachment in attachments:
                if attachment['@odata.type'] == "#microsoft.graph.fileAttachment":
                    file_name = attachment['name']
                    file_content = attachment['contentBytes'] # noqa
                    # file_path = os.path.join(ATTACHMENT_DIR, file_name)

                    # with open(file_path, "wb") as file:
                    #     file.write(bytes(file_content))

                    print(f"Attachment saved: {file_name}")
        else:
            print(f"Error fetching attachments: {response.status_code} - {response.text}")

def test():
    """ Shows basic usage of the Outlook API.
        Lists the user's mails.
    """
    service = Outlook()
    try:
        service.get_emails() if service.authenticate() else None

    except Exception as error:
        # TODO (developer) - Handle errors from API.
        print(f"An error occurred: {error}")
