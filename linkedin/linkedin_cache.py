"""
LinkedIn Cache

Thread-safe in-process cache for LinkedIn HTML.
Cache key: linkedin_url
"""

from threading import Lock

_CACHE = {}
_LOCK = Lock()


def get_cached_html(linkedin_url):
    with _LOCK:
        return _CACHE.get(linkedin_url)


def set_cached_html(linkedin_url, html):
    with _LOCK:
        _CACHE[linkedin_url] = html


def is_cached(linkedin_url):
    with _LOCK:
        return linkedin_url in _CACHE
