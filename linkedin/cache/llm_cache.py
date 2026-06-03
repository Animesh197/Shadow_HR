"""
LLM Extraction Cache

Caches LLM extraction results to avoid repeated API calls.
"""

import hashlib
import json
from threading import Lock


# In-memory cache
_llm_cache = {}
_cache_lock = Lock()


def get_cache_key(linkedin_url):
    """
    Generate cache key from LinkedIn URL.
    
    Args:
        linkedin_url (str): LinkedIn profile URL
    
    Returns:
        str: Hash of URL
    """
    return hashlib.sha256(linkedin_url.encode()).hexdigest()


def get_cached_extraction(linkedin_url):
    """
    Get cached extraction result.
    
    Args:
        linkedin_url (str): LinkedIn profile URL
    
    Returns:
        dict or None: Cached extraction result or None if not cached
    """
    cache_key = get_cache_key(linkedin_url)
    
    with _cache_lock:
        return _llm_cache.get(cache_key)


def set_cached_extraction(linkedin_url, extraction_result):
    """
    Cache extraction result.
    
    Args:
        linkedin_url (str): LinkedIn profile URL
        extraction_result (dict): Extraction result to cache
    """
    cache_key = get_cache_key(linkedin_url)
    
    with _cache_lock:
        _llm_cache[cache_key] = extraction_result


def is_cached(linkedin_url):
    """
    Check if extraction result is cached.
    
    Args:
        linkedin_url (str): LinkedIn profile URL
    
    Returns:
        bool: True if cached
    """
    cache_key = get_cache_key(linkedin_url)
    
    with _cache_lock:
        return cache_key in _llm_cache


def clear_cache():
    """Clear all cached extraction results."""
    with _cache_lock:
        _llm_cache.clear()
