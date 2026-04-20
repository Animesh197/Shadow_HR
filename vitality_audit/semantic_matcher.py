from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# load once (IMPORTANT)
model = SentenceTransformer('all-MiniLM-L6-v2')

# Embedding cache to avoid re-encoding the same text
_embedding_cache = {}

def _get_embedding(text):
    if text not in _embedding_cache:
        _embedding_cache[text] = model.encode([text])[0]
    return _embedding_cache[text]


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