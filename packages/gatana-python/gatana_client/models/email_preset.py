from enum import Enum


class EmailPreset(str, Enum):
    FASTMAIL = "fastmail"
    GMAIL = "gmail"
    ICLOUD = "icloud"
    IMAP = "imap"
    JMAP = "jmap"
    MICROSOFT365 = "microsoft365"

    def __str__(self) -> str:
        return str(self.value)
