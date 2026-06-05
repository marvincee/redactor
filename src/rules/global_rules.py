import re
from src.vault import RedactionVault

# Email regex pattern (Unicode-safe boundaries)
EMAIL_REGEX = re.compile(
    r'(?<![A-Za-z0-9._%+-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![A-Za-z0-9])'
)

# Korean phone number regex pattern:
# Matches: 010-1234-5678, 02-123-4567, +82-10-1234-5678, 01012345678, etc.
# Uses (?!\d) at the end to allow Korean grammatical particles to be attached directly (e.g. 010-1234-5678이다)
KOREAN_PHONE_REGEX = re.compile(
    r'(?<!\w)(?:\+82[-.\s]?(?:\(0\))?[-.\s]?|0)(?:10|11|16|17|18|19|2|[3-6][1-9]|70|80)[-.\s]?\d{3,4}[-.\s]?\d{4}(?!\d)'
)

# German phone number regex pattern:
# Matches: +49 170 1234567, 0170-1234567, 030/123456, etc.
# Uses (?!\d) at the end to allow correct trailing bounds
GERMAN_PHONE_REGEX = re.compile(
    r'(?<!\w)(?:\+49[-.\s]?(?:\(0\))?[-.\s]?|0049[-.\s]?(?:\(0\))?[-.\s]?|0)[1-9][0-9]{1,4}[-.\s/]*\d{3,9}(?:[-.\s]?\d{1,4})*(?!\d)'
)

# Standard URL regex pattern:
# Matches standard HTTP/HTTPS URLs and www. links
URL_REGEX = re.compile(
    r'(?i)(?<![A-Za-z0-9])(?:https?://|www\.)[A-Za-z0-9+&@#/%?=~_|!:,.;-]*[A-Za-z0-9+&@#/%=~_|]'
)

def redact_emails(text: str, vault: RedactionVault) -> str:
    """Finds all email addresses in text, registers them in the vault, and replaces them with their token."""
    def replace_email(match):
        email = match.group(0)
        token = vault.get_or_create_token(email, "EMAIL")
        return token
    return EMAIL_REGEX.sub(replace_email, text)

def redact_phones(text: str, vault: RedactionVault) -> str:
    """Finds all Korean and German phone numbers in text, registers them in the vault, and replaces them with their token."""
    def replace_phone(match):
        phone = match.group(0)
        token = vault.get_or_create_token(phone, "PHONE")
        return token

    # Redact Korean phone numbers first
    text = KOREAN_PHONE_REGEX.sub(replace_phone, text)
    # Then redact German phone numbers
    text = GERMAN_PHONE_REGEX.sub(replace_phone, text)
    return text

def redact_urls(text: str, vault: RedactionVault) -> str:
    """Finds all URLs in text, registers them in the vault, and replaces them with their token."""
    def replace_url(match):
        url = match.group(0)
        token = vault.get_or_create_token(url, "URL")
        return token
    return URL_REGEX.sub(replace_url, text)

def redact_all(text: str, vault: RedactionVault) -> str:
    """Runs all global rule redactions (emails, phone numbers, and URLs) sequentially."""
    text = redact_emails(text, vault)
    text = redact_phones(text, vault)
    text = redact_urls(text, vault)
    return text
