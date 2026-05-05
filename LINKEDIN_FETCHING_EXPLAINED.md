# LinkedIn Fetching Process - Complete Explanation

## Overview

We **DO NOT use LinkedIn's official API**. Instead, we use **web scraping** with a headless browser (Playwright) to fetch LinkedIn profile HTML, then parse it to extract education and experience data.

## Why Not Use LinkedIn API?

1. **No Public API Access**: LinkedIn's official API is restricted and requires special partnership agreements
2. **Limited Data**: Even with API access, the data available is limited
3. **Rate Limits**: API has strict rate limits
4. **Cost**: API access often requires paid plans

## Our Approach: Web Scraping with Playwright

### Technology Stack

```
Playwright (Browser Automation)
    ↓
Chromium Browser (Headless)
    ↓
LinkedIn Profile Page (HTML)
    ↓
BeautifulSoup (HTML Parsing)
    ↓
Structured Data (JSON)
```

---

## Step-by-Step Process

### Step 1: One-Time Session Setup

**File:** `linkedin/save_session.py`

**Purpose:** Save LinkedIn login session cookies for future use

**How it works:**
```python
# Run this ONCE manually
python linkedin/save_session.py
```

**What happens:**
1. Opens a **visible** Chromium browser window
2. Navigates to `https://www.linkedin.com/login`
3. **You manually log in** with your LinkedIn credentials
4. After login, you press Enter in the terminal
5. Playwright saves all cookies and session data to `linkedin_session.json`
6. This file is used for all future fetches (no need to log in again)

**Session File Structure:**
```json
{
  "cookies": [
    {
      "name": "li_at",
      "value": "your_session_token",
      "domain": ".linkedin.com",
      ...
    },
    ...
  ],
  "origins": [...]
}
```

**Important:**
- `linkedin_session.json` is gitignored (contains your credentials)
- Session expires after ~1 year (LinkedIn's policy)
- If session expires, run `save_session.py` again

---

### Step 2: Fetching LinkedIn Profile HTML

**File:** `linkedin/linkedin_fetcher.py`

**Function:** `fetch_linkedin_html(linkedin_url)`

**Process:**

#### 2.1 Check Cache
```python
if is_cached(linkedin_url):
    return get_cached_html(linkedin_url), "success"
```
- First checks in-memory cache to avoid redundant fetches
- Cache is per-session (cleared when program restarts)

#### 2.2 Rate Limiting
```python
MIN_DELAY = 3  # seconds between fetches
```
- Enforces 3-second delay between LinkedIn requests
- Prevents triggering LinkedIn's bot detection
- Thread-safe using locks

#### 2.3 Launch Browser
```python
browser = p.chromium.launch(
    headless=True,  # No visible window
    args=["--no-sandbox", "--disable-dev-shm-usage"]
)
```
- Uses Chromium browser (same as Chrome)
- Runs in headless mode (no GUI)
- Special flags for Docker/server compatibility

#### 2.4 Load Session
```python
context_kwargs = {
    "user_agent": "Mozilla/5.0 ...",  # Pretend to be Chrome
    "viewport": {"width": 1280, "height": 800}
}

if session_file and os.path.exists(session_file):
    context_kwargs["storage_state"] = session_file
```
- Loads saved cookies from `linkedin_session.json`
- Sets realistic user agent (pretends to be Chrome browser)
- Sets viewport size (important for responsive content)

#### 2.5 Apply Stealth Mode
```python
from playwright_stealth import Stealth
Stealth().apply_stealth_sync(page)
```
- Masks browser automation fingerprints
- Bypasses LinkedIn's bot detection (PerimeterX)
- Makes the browser look like a real human user

**What it does:**
- Removes `navigator.webdriver` flag
- Spoofs Chrome plugins
- Fakes canvas fingerprints
- Mimics real browser behavior

#### 2.6 Navigate to Profile
```python
page.goto(
    linkedin_url,
    timeout=15000,  # 15 seconds
    wait_until="domcontentloaded"
)
```
- Opens the LinkedIn profile URL
- Waits for DOM to load (not full page load)
- 15-second timeout to prevent hanging

#### 2.7 Wait for JavaScript Rendering
```python
page.wait_for_timeout(4000)  # 4 seconds
```
- LinkedIn uses heavy JavaScript to render content
- Waits 4 seconds for React/JS to render profile sections
- Critical for getting complete HTML

#### 2.8 Extract HTML
```python
html = page.content()
```
- Gets the fully rendered HTML (after JavaScript execution)
- Includes all dynamically loaded content
- Returns complete page source

#### 2.9 Detect Auth Wall
```python
if _is_blocked(html):
    return html, "blocked"
```
- Checks if LinkedIn returned login page instead of profile
- Looks for keywords: "join now", "sign in", "authwall", "captcha"
- If 2+ block signals found, session is invalid

#### 2.10 Cache and Return
```python
set_cached_html(linkedin_url, html)
return html, "success"
```
- Saves HTML to in-memory cache
- Returns HTML and success status

---

### Step 3: Parsing HTML to Extract Data

**File:** `linkedin/linkedin_parser.py`

**Function:** `parse_linkedin_profile(html)`

**Process:**

#### 3.1 Parse HTML with BeautifulSoup
```python
soup = BeautifulSoup(html, 'html.parser')
visible_text = soup.get_text(separator='|', strip=True)
```
- Converts HTML to parseable object
- Extracts all visible text with `|` separators
- Removes HTML tags, keeps only content

#### 3.2 Extract Profile Sections
```python
profile = {
    "name": extract_name(soup),
    "headline": extract_headline(soup, visible_text),
    "location": extract_location(soup, visible_text),
    "experience": extract_experience(soup, visible_text),
    "education": extract_education(soup, visible_text)
}
```

**How each section is extracted:**

**Name:**
- Looks in `<title>` tag: "Name | LinkedIn"
- Fallback: searches for `<h1>` tags

**Headline:**
- Finds long text (50-500 chars) after name
- Filters out locations and UI elements

**Location:**
- Looks for "City, State, Country" pattern
- Uses regex: `^[A-Z][a-z]+,\s*[A-Z][a-z]+`

**Experience:**
- Searches for lines with "at", "@", "·", "•" separators
- Format: "Role at Company"
- Extracts dates using regex: `Jan 2024 - Present`
- Filters out UI noise, achievements, projects

**Education:**
- Searches for institution keywords: "University", "Institute", "College", "School", "IIT", "NIT"
- Validates each line to reject:
  - Hashtags (#NewtonSchool)
  - Social media posts ("Big thanks to...")
  - Activity descriptions ("Student at...")
  - UI elements
- Extracts degree and year from nearby lines

---

### Step 4: Normalization

**File:** `linkedin/linkedin_normalizer.py`

**Purpose:** Make resume ↔ LinkedIn comparisons robust

**Examples:**

**Company Names:**
```python
"Microsoft Corporation" → "microsoft"
"Google India Pvt Ltd" → "google"
"Tata Consultancy Services" → "tcs"
```

**Institution Names:**
```python
"Indian Institute of Technology, Patna" → "iit patna"
"IIT Patna" → "iit patna"
"Newton School of Technology, Rishihood University" → "newton"
```

**Process:**
1. Convert to lowercase
2. Remove legal suffixes (Corp, Inc, Ltd, Pvt Ltd)
3. Remove common words (University, Institute, College)
4. Handle special cases (IIT, NIT, BITS)
5. Match against known aliases

---

### Step 5: Matching

**File:** `linkedin/linkedin_matcher.py`

**Purpose:** Compare resume data with LinkedIn data

**Matching Logic:**

**Identity Match:**
- Compares names (exact, partial, fuzzy)
- Score: 0-100%

**Experience Match:**
- Normalizes company names
- Checks if resume companies appear on LinkedIn
- Score: (matched / total) × 100

**Education Match:**
- Normalizes institution names
- Checks if resume institutions appear on LinkedIn
- Score: (matched / total) × 100

**Timeline Consistency:**
- Checks for overlapping employment
- Validates date ranges
- Score: 0-100%

---

## Complete Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER RUNS: python linkedin/save_session.py (ONE TIME)   │
│    - Opens browser                                           │
│    - User logs in manually                                   │
│    - Saves cookies to linkedin_session.json                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. MAIN PIPELINE: python main.py                            │
│    - Extracts LinkedIn URL from resume PDF                   │
│    - Calls fetch_linkedin_html(url)                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. FETCHER: linkedin/linkedin_fetcher.py                    │
│    ✓ Check cache (in-memory)                                │
│    ✓ Rate limit (3 sec delay)                               │
│    ✓ Launch Chromium browser (headless)                     │
│    ✓ Load session cookies                                   │
│    ✓ Apply stealth mode                                     │
│    ✓ Navigate to LinkedIn profile                           │
│    ✓ Wait 4 seconds for JS rendering                        │
│    ✓ Extract HTML                                           │
│    ✓ Detect auth wall                                       │
│    ✓ Cache HTML                                             │
│    ✓ Return HTML + status                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. PARSER: linkedin/linkedin_parser.py                      │
│    ✓ Parse HTML with BeautifulSoup                          │
│    ✓ Extract name from <title>                              │
│    ✓ Extract headline (long text after name)                │
│    ✓ Extract location (City, State pattern)                 │
│    ✓ Extract experience (Role at Company)                   │
│    ✓ Extract education (Institution names)                  │
│    ✓ Filter out hashtags, posts, UI noise                   │
│    ✓ Return structured profile dict                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. NORMALIZER: linkedin/linkedin_normalizer.py              │
│    ✓ Normalize company names                                │
│    ✓ Normalize institution names                            │
│    ✓ Handle abbreviations (IIT, NIT, TCS)                   │
│    ✓ Remove suffixes (Corp, Ltd, University)                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 6. MATCHER: linkedin/linkedin_matcher.py                    │
│    ✓ Compare resume ↔ LinkedIn                              │
│    ✓ Identity match (name)                                  │
│    ✓ Experience match (companies)                           │
│    ✓ Education match (institutions)                         │
│    ✓ Timeline consistency                                   │
│    ✓ Calculate match scores                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 7. SCORER: linkedin/linkedin_scorer.py                      │
│    ✓ Generate signals from matches                          │
│    ✓ Route by candidate type (fresher/experienced)          │
│    ✓ Calculate LinkedIn score (0-100)                       │
│    ✓ Determine confidence level                             │
│    ✓ Merge with GitHub score                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│ 8. OUTPUT: Final verification report                        │
│    - Identity Match: 100%                                    │
│    - Experience Match: 75%                                   │
│    - Education Match: 100%                                   │
│    - LinkedIn Score: 85/100                                  │
│    - Final Score: GitHub (75%) + LinkedIn (25%)             │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Technologies

### 1. Playwright
- **What:** Browser automation library (like Selenium, but better)
- **Why:** Can execute JavaScript, handle dynamic content
- **Alternative:** Selenium, Puppeteer

### 2. Playwright Stealth
- **What:** Plugin to hide automation fingerprints
- **Why:** LinkedIn uses PerimeterX bot detection
- **How:** Removes `navigator.webdriver`, spoofs plugins, fakes fingerprints

### 3. BeautifulSoup
- **What:** HTML parsing library
- **Why:** Easy to extract text and elements from HTML
- **Alternative:** lxml, html.parser

### 4. Session Cookies
- **What:** Authentication tokens saved from manual login
- **Why:** LinkedIn requires login to view full profiles
- **Format:** Playwright storage_state.json

---

## Advantages of Our Approach

✅ **No API Required** - Works without LinkedIn partnership
✅ **Full Data Access** - Gets all visible profile data
✅ **No Rate Limits** - Only limited by bot detection
✅ **Free** - No API costs
✅ **Flexible** - Can extract any visible data

## Disadvantages

❌ **Fragile** - Breaks if LinkedIn changes HTML structure
❌ **Slow** - Browser automation takes 5-10 seconds per profile
❌ **Session Management** - Requires manual login, session expires
❌ **Bot Detection Risk** - LinkedIn may block if detected
❌ **Ethical/Legal Gray Area** - Violates LinkedIn's Terms of Service

---

## Security & Privacy

### What We Store:
- ✅ Session cookies (local only, gitignored)
- ✅ Cached HTML (in-memory, temporary)
- ❌ No passwords stored
- ❌ No user credentials

### What LinkedIn Sees:
- Your IP address
- Your user agent (Chrome browser)
- Your session cookies
- Profile views (shows up in "Who viewed your profile")

### Recommendations:
1. Use a dedicated LinkedIn account for scraping
2. Don't scrape too frequently (respect rate limits)
3. Add delays between requests
4. Use residential proxies if scaling
5. Be aware this violates LinkedIn's ToS

---

## Troubleshooting

### Issue: "Blocked by auth wall"
**Cause:** Session expired or invalid
**Fix:** Run `python linkedin/save_session.py` again

### Issue: "playwright-stealth not installed"
**Cause:** Missing dependency
**Fix:** `pip install playwright-stealth`

### Issue: "No education extracted"
**Cause:** LinkedIn lazy loading not triggered
**Fix:** Increase `WAIT_AFTER_LOAD` or add scrolling

### Issue: "Bot detection / CAPTCHA"
**Cause:** Too many requests, suspicious behavior
**Fix:** 
- Increase `MIN_DELAY`
- Use residential proxy
- Wait 24 hours before retrying

---

## Environment Variables

```bash
# .env file
LINKEDIN_SESSION_FILE=linkedin_session.json
```

**Required:** Yes
**Purpose:** Path to saved session cookies
**Generate:** Run `python linkedin/save_session.py`

---

## Files Overview

```
linkedin/
├── save_session.py          # One-time session setup
├── linkedin_fetcher.py      # Fetch HTML with Playwright
├── linkedin_cache.py        # In-memory cache
├── linkedin_parser.py       # Parse HTML to structured data
├── linkedin_normalizer.py   # Normalize names for matching
├── linkedin_matcher.py      # Compare resume ↔ LinkedIn
├── linkedin_scorer.py       # Calculate verification score
└── linkedin_signals.py      # Generate verification signals

linkedin_session.json        # Saved cookies (gitignored)
```

---

## Summary

We use **web scraping** (not API) to fetch LinkedIn profiles:

1. **One-time setup:** Save login session cookies
2. **Fetch:** Use Playwright to open profile in headless browser
3. **Parse:** Extract education/experience from HTML
4. **Normalize:** Standardize names for comparison
5. **Match:** Compare with resume data
6. **Score:** Calculate verification score

This approach works without LinkedIn API access but requires careful handling to avoid bot detection.
