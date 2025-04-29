import re
from ftfy import fix_text

def clean_text(text):
    # Normalize unicode characters
    text = fix_text(text)
    # Lowercase
    text = text.lower()
    # Remove URLs
    text = re.sub(r'(https?://\S+)|(www\.\S+)', '', text)
    # Remove punctuation (preserving only word chars and spaces)
    text = re.sub(r'[^a-zA-Z0-9\s]', '', text)
    # Remove newline, tab, etc.
    text = re.sub(r'[\n\r\t]', ' ', text)
    # Remove extra spaces
    text = " ".join(text.split())

    return text