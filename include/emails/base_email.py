from abc import ABC, abstractmethod
from typing import Generator

class EmailService(ABC):
    """Abstract base class for all email services"""

    __slots__ = []

    @abstractmethod
    def authenticate(self) -> bool:
        ...

    @abstractmethod
    def save_attachment(self, msg_id):
        ...

    @abstractmethod
    def get_emails(self, max_results) -> Generator[tuple[dict, list[dict]], None, None]:
        """Yield headers and body of an email
            headers is a key-value dict
            body is a list of content-type and message dict
                content-type may contain charset information (e.g., text/html; charset=utf-8)
        """
        ...
