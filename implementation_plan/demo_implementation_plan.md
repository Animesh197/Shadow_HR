# Fix: Live Demo Detection Inconsistency

## Root Cause

`check_valid_demo_for_project` (repo_selector.py:68) normalizes the **entire** project name including parenthetical text, making it too long to match any demo URL.

### Exact failure trace for ritesh.pdf → project "WAR (WashingAtRishihood)"

| Step | Value |
|------|-------|
| `best_repo` | `war` (homepage: `null`) |
| **Path 1:** `is_demo_url_valid(None, ...)` | → `False` (line 51: `if not url: return False`) |
| **Path 2:** `normalize("WAR (WashingAtRishihood)")` | → `"warwashingatrishihood"` |
| Demo URL `war-frontend.vercel.app` normalized | → `"warfrontendvercelapp"` |
| `"warwashingatrishihood"` in `"warfrontendvercelapp"` | → **False** ❌ |
| **Result** | `live_demo = False` |

The working demo `war-frontend.vercel.app` (score: 3, interactive: True) is never linked back to the project because the substring check fails.

### Why resume2.pdf works

resume2.pdf projects have simple names without parenthetical expansions (e.g. `"Travel Story"`). `normalize("Travel Story")` → `"travelstory"`, which IS a substring of `normalize("travel-story.vercel.app")` → `"travelstoryvercelapp"` ✅.

## The single bug

[check_valid_demo_for_project](file:///Users/animeshkumarrai/Desktop/AI/resume_auditor/vitality_audit/repo_selector.py#L68-L80) uses the full project name (including parenthetical expansions) as a substring search against demo URLs. When the LLM extracts project names like `"WAR (WashingAtRishihood)"`, the normalized form `"warwashingatrishihood"` never appears in any URL.

## Proposed Fix — 2 changes in 1 file

### [MODIFY] [repo_selector.py](file:///Users/animeshkumarrai/Desktop/AI/resume_auditor/vitality_audit/repo_selector.py)

**Change 1** (lines 68–80): Strip parenthetical from project name before matching:

```diff
 def check_valid_demo_for_project(project, demo_results):
-    proj_norm = normalize(project)
+    # Try full name, then core name (before any parenthetical)
+    names_to_try = [project]
+    if "(" in project:
+        core = project.split("(")[0].strip()
+        if core:
+            names_to_try.append(core)
 
     for d in demo_results:
         if d.get("score", 0) <= 0:
             continue
 
         url_norm = normalize(d.get("url", ""))
 
-        if proj_norm in url_norm:
-            return True
+        for name in names_to_try:
+            proj_norm = normalize(name)
+            if proj_norm and proj_norm in url_norm:
+                return True
 
     return False
```

**Change 2** (lines 228–231): Also check the matched **repo name** against demo URLs — this is a safety net because repo names are inherently URL-friendly:

```diff
             homepage_demo = is_demo_url_valid(best_repo.get("homepage"), demo_results)
             proj_demo = check_valid_demo_for_project(proj, demo_results)
+            repo_demo = check_valid_demo_for_project(best_repo.get("name", ""), demo_results)

-            live_demo = homepage_demo or proj_demo
+            live_demo = homepage_demo or proj_demo or repo_demo
```

### After fix — WAR trace:

| Step | Value |
|------|-------|
| Path 1: `is_demo_url_valid(None, ...)` | → `False` |
| Path 2: Full name `"warwashingatrishihood"` in URLs | → `False` |
| Path 2: Core name `normalize("WAR")` = `"war"` in `"warfrontendvercelapp"` | → **True** ✅ |
| **Result** | `live_demo = True` |

## Verification

- Run `python main.py` (with ritesh.pdf)
- Confirm WAR project shows `live_demo: True`
- Confirm SabApplier-AI stays `live_demo: False` (homepage returns 404, that's correct — demo IS broken)
