import re


def clean_text(text: str) -> str:
    """Normalize raw extracted text."""
    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    # Remove weird unicode chars (keep basic latin + punctuation)
    text = text.encode("ascii", "ignore").decode("ascii")
    # Strip leading/trailing whitespace
    text = text.strip()
    return text
