# ============================================================
# PHASE 8 — SHARED GITHUB CACHE
# ============================================================
# Goal:
# Prevent repeated API calls for same file.
# ============================================================

from threading import Lock


# global cache
_FILE_CACHE = {}
_CACHE_LOCK = Lock()


def get_cached_file(owner, repo, path):

    key = f"{owner}/{repo}/{path}"

    with _CACHE_LOCK:
        return _FILE_CACHE.get(key)


def set_cached_file(owner, repo, path, content):

    key = f"{owner}/{repo}/{path}"

    with _CACHE_LOCK:
        _FILE_CACHE[key] = content


def clear_cache():
    global _FILE_CACHE

    with _CACHE_LOCK:
        _FILE_CACHE = {}