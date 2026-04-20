# Fix Resume-to-Repo Matching & Performance

## Problem Summary

**Matching failures:** Projects like "Quick Serve" fail to match `capstone_03_QuickServe` because:
1. `normalize_text` strips `_` and `-` but doesn't split camelCase → tokens `["capstone", "03", "quickserve"]` never contain `"quick"` or `"serve"` separately.
2. `candidate_generator` uses `token_overlap_score` which requires token-level matches — but `"quickserve"` ≠ `"quick"` + `"serve"`.
3. The `generate_candidates` gate (`score > 0`) means if no token overlaps, the repo never becomes a candidate, so semantic matching and `fuzzy_substring_score` never fire.
4. Prefilter uses the same broken `normalize()` (removes all separators) so doesn't help either.

**Performance issues:**
1. `compute_semantic_similarity` encodes text one-at-a-time, called **3× per candidate** × N candidates. Each call to `model.encode()` is a separate forward pass.
2. `fetch_readme` in `repo_selector.py` (line 153) does NOT use the GitHub token → may hit rate limits faster, and also duplicates the `fetch_readme` already in `readme_analyzer.py`.
3. `readme_analyzer.analyze_readme_alignment` fetches the README *again* inside the enrichment loop (line 372), despite it already being cached.
4. `infra_analyzer.check_repo_infra` makes up to 3 API calls per repo (root, shallow subfolders, full tree).

---

## Proposed Changes

### 1. Text Normalization — Fix camelCase & prefix splitting

#### [MODIFY] [text_utils.py](file:///Users/animeshkumarrai/Desktop/AI/resume_auditor/vitality_audit/matching/text_utils.py)

Add camelCase splitting to `normalize_text` so `"QuickServe"` → `"quick serve"` and `"capstone_03_QuickServe"` → `"capstone 03 quick serve"`:

```diff
 def normalize_text(text):
     if not text:
         return ""
+    # Split camelCase: "QuickServe" → "Quick Serve"
+    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)
+    text = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', text)
     text = text.lower()
     text = re.sub(r'[^a-z0-9\s]', ' ', text)
     return text.strip()
```

Add a new `normalized_contains` function for the critical substring check:

```python
def normalized_contains(project, repo_name):
    """Check if normalized project name is contained in normalized repo name."""
    a = re.sub(r'[^a-z0-9]', '', normalize_text(project))
    b = re.sub(r'[^a-z0-9]', '', normalize_text(repo_name))
    return a in b or b in a
```

---

### 2. Candidate Generator — Never miss prefix/renamed repos

#### [MODIFY] [candidate_generator.py](file:///Users/animeshkumarrai/Desktop/AI/resume_auditor/vitality_audit/matching/candidate_generator.py)

Add `normalized_contains` as a fallback so repos like `capstone_03_QuickServe` always become candidates:

```diff
-from .text_utils import token_overlap_score
+from .text_utils import token_overlap_score, normalized_contains

 def generate_candidates(project, repos, top_k=5):
     scored = []

     for repo in repos:
         name = repo.get("name", "")
         desc = repo.get("description", "")

         score = (
             token_overlap_score(project, name) * 2 +
             token_overlap_score(project, desc)
         )

+        # Ensure prefixed/renamed repos are never missed
+        if score == 0 and normalized_contains(project, name):
+            score = 1.5  # strong enough to become a candidate

         if score > 0:
             scored.append((repo, score))
```

---

### 3. Semantic Matcher — Batch encoding for performance

#### [MODIFY] [semantic_matcher.py](file:///Users/animeshkumarrai/Desktop/AI/resume_auditor/vitality_audit/semantic_matcher.py)

Batch-encode all texts at once instead of encoding them one-at-a-time per call:

```python
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
    """Returns similarity score (0–1)"""
    if not text1 or not text2:
        return 0

    emb1 = _get_embedding(text1)
    emb2 = _get_embedding(text2)

    score = cosine_similarity([emb1], [emb2])[0][0]
    return float(score)
```

> **Why:** The project name `"Quick Serve"` gets re-encoded once per candidate (3 calls × N repos). With caching, it's encoded once total. README content gets encoded only once per repo too.

---

### 4. Prefilter normalization — Fix to use camelCase-aware matching

#### [MODIFY] [repo_selector.py](file:///Users/animeshkumarrai/Desktop/AI/resume_auditor/vitality_audit/repo_selector.py)

**Change 1 (line 35-36):** Replace the local `normalize()` with the fixed one from `text_utils`:

```diff
-def normalize(text):
-    return text.lower().replace(" ", "").replace("-", "").replace("_", "")
+from vitality_audit.matching.text_utils import normalize_text, normalized_contains
+def normalize(text):
+    """Strip-all-separators normalize for backwards compat."""
+    return normalize_text(text).replace(" ", "")
```

**Change 2 (line 153-170):** Use auth token for `fetch_readme` and reuse the one from `readme_analyzer`:

```diff
-def fetch_readme(owner, repo):
-    """
-    Fetch README content (lightweight)
-    """
-    url = f"https://api.github.com/repos/{owner}/{repo}/readme"
-
-    headers = {
-        "Accept": "application/vnd.github.v3.raw"
-    }
-
-    try:
-        res = requests.get(url, headers=headers, timeout=5)
-        if res.status_code == 200:
-            return res.text[:3000]  # limit size
-    except:
-        pass
-
-    return ""
+from vitality_audit.readme_analyzer import fetch_readme as _fetch_readme_raw
+
+def fetch_readme(owner, repo):
+    """Fetch README content (uses authenticated call from readme_analyzer)."""
+    content = _fetch_readme_raw(owner, repo)
+    return content[:3000] if content else ""
```

**Change 3 (line 204-209):** Fix fallback match to also use `normalized_contains`:

```diff
         if not best_repo:
             for repo in repos:
-                if normalize(proj) in normalize(repo.get("name", "")):
+                if normalized_contains(proj, repo.get("name", "")):
                     best_repo = repo
                     best_score = 0.5
                     confidence_label = "rule_based_override"
                     break
```

**Change 4 (line 308-311):** Fix prefilter project match similarly:

```diff
         for proj in projects:
-            if normalize(proj) in normalize(repo_name):  # ✅ fixed
+            if normalized_contains(proj, repo_name):
                 score += 10
```

**Change 5 (line 212):** Accept `rule_based_override` in the decision gate:

```diff
-        if best_repo and confidence_label in ["high_confidence", "medium_confidence", "low_confidence"]:
+        if best_repo and confidence_label in ["high_confidence", "medium_confidence", "low_confidence", "rule_based_override"]:
```

---

## Why This Fixes "Quick Serve" → `capstone_03_QuickServe`

| Step | Before | After |
|------|--------|-------|
| `normalize_text("capstone_03_QuickServe")` | `"capstone 03 quickserve"` | `"capstone 03 quick serve"` |
| `tokenize` | `["capstone", "03", "quickserve"]` | `["capstone", "03", "quick", "serve"]` |
| `token_overlap_score("Quick Serve", ...)` | 0 (no overlap) | 1.0 (`{"quick","serve"}` ⊂ tokens) |
| Candidate generated? | ❌ No | ✅ Yes |
| `fuzzy_substring_score` fires? | Never reached | `"quick serve"` in `"capstone 03 quick serve"` → 1.0 |
| Final score | 0 | `40 (name_exact) + 25 (name_overlap) + semantic ≈ 75+` → `high_confidence` |

---

## Performance Impact Summary

| Bottleneck | Before | After |
|------------|--------|-------|
| Semantic encoding | 3 calls per candidate × N candidates (each a forward pass) | Cached — each unique text encoded once |
| `fetch_readme` in repo_selector | Unauthenticated, may hit rate limits | Reuses authenticated `readme_analyzer.fetch_readme` |
| `analyze_readme_alignment` in enrichment | Fetches README again (already cached in matching step) | No change needed — enrichment loop is on prefiltered repos (≤8), acceptable |

---

## Open Questions

None — these are targeted fixes to existing logic. No architectural changes.

## Verification Plan

### Manual Test
- Run `python main.py` against `resume1.pdf`
- Confirm "Quick Serve" (and similar prefixed projects) now show `status: "found"` 
- Confirm prefilter logs show correct scores for prefixed repos
- Confirm runtime reduction (fewer encode calls visible in timing)
