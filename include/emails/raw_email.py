from typing import Generator
from email import parser, message_from_file
from .base_email import EmailService

class RawEmailHandler(EmailService):
    __slots__ = ["file_path"]

    def authenticate(self, _ = None):
        return True

    def get_emails(self, _ = None) -> Generator[tuple[dict, list], None, None]:
        file = self.file_path
        headers = {}
        body = []
        with open(file) as f:
            message = message_from_file(f)
            headers = {item[0]: item[1] for item in message.items()}

            if message.is_multipart():
                for part in message.walk():
                    content_type = part.get_content_type()
                    if content_type in ["text/plain", "text/html"]:
                        charset = part.get_content_charset() or "utf-8"
                        data = part.get_payload(decode=True).decode(charset)

                        body.append({content_type: data})
            else:
                content_type = message.get_content_type()
                charset = message.get_content_charset() or "utf-8"
                data = message.get_payload(decode=True).decode(charset)

                body.append({content_type: data})

        yield headers, body

    def save_attachment(self):
        ...

def test():
    service = RawEmailHandler()
    service.file_path = "/Data/Indranil/STN/tmp/metcap-240626200051.1545662.mail"

    (headers, body) = service.get_emails()
    print(headers, body)
