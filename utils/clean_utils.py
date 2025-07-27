import re

def clean_text(raw_text):
    # Remove extra whitespaces and non-printable characters
    cleaned = re.sub(r'\s+', ' ', raw_text)
    cleaned = re.sub(r'[^\x20-\x7E]+', ' ', cleaned)
    return cleaned.strip()
