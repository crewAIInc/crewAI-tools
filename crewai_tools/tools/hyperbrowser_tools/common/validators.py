from urllib.parse import urlparse


def validate_url(url: str):
    if not url.startswith(("http://", "https://")):
        raise ValueError("Invalid URL. URL must start with 'http://' or 'https://'")

    parsed_url = urlparse(url)
    if not parsed_url.netloc:
        raise ValueError("Invalid URL. URL must contain a valid domain")
