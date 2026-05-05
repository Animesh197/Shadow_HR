import re

def is_noise(text: str) -> bool:
    if not text:
        return True

    text_lower = text.lower()

    noise_keywords = [
        '#', 'thanks', 'followers', 'connections',
        'comment', 'like', 'share', 'post', 'react'
    ]

    if any(k in text_lower for k in noise_keywords):
        return True

    if len(text.split()) > 12:
        return True

    return False


def is_valid_text(text: str, min_len=3, max_len=120):
    return text and min_len <= len(text.strip()) <= max_len


def clean_text(text: str):
    text = re.sub(r'\s+', ' ', text)
    return text.strip()