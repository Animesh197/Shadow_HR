from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from threading import Lock

# load once
model = SentenceTransformer('all-MiniLM-L6-v2')

# Thread-safe embedding cache
_embedding_cache = {}
_cache_lock = Lock()


def _get_embedding(text):
    with _cache_lock:
        if text in _embedding_cache:
            return _embedding_cache[text]

    emb = model.encode([text])[0]

    with _cache_lock:
        _embedding_cache[text] = emb

    return emb


def batch_precompute_embeddings(texts):
    """
    Encode a list of texts in one batch call.
    Stores results in cache so subsequent compute_semantic_similarity calls are instant.
    """
    uncached = []
    with _cache_lock:
        for t in texts:
            if t and t not in _embedding_cache:
                uncached.append(t)

    if uncached:
        embeddings = model.encode(uncached, batch_size=32, show_progress_bar=False)
        with _cache_lock:
            for t, emb in zip(uncached, embeddings):
                _embedding_cache[t] = emb


def compute_semantic_similarity(text1, text2):
    """
    Returns similarity score (0–1)
    """
    if not text1 or not text2:
        return 0

    emb1 = _get_embedding(text1)
    emb2 = _get_embedding(text2)

    score = cosine_similarity([emb1], [emb2])[0][0]
    return float(score)