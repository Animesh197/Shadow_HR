import re

def normalize_text(text):
    if not text:
        return ""
    # Split camelCase: "QuickServe" → "Quick Serve"
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
    text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', text)
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return text.strip()


def tokenize(text):
    return normalize_text(text).split()


def token_overlap_score(a, b):
    tokens_a = set(tokenize(a))
    tokens_b = set(tokenize(b))

    if not tokens_a or not tokens_b:
        return 0

    overlap = tokens_a.intersection(tokens_b)
    return len(overlap) / max(len(tokens_a), len(tokens_b))


def normalized_contains(project, repo_name):
    """Check if normalized project appears inside normalized repo name (ignoring all separators)."""
    a = re.sub(r'[^a-z0-9]', '', normalize_text(project))
    b = re.sub(r'[^a-z0-9]', '', normalize_text(repo_name))
    return a in b or b in a


def fuzzy_substring_score(a, b):
    """
    Handles reordered / partial matches
    """
    a = normalize_text(a)
    b = normalize_text(b)

    if a in b or b in a:
        return 1.0

    return 0