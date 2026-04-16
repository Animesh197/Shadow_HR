"""
Responsible for:
- Extracting GitHub username from links
- Normalizing GitHub username (LLM vs links priority)
"""

def extract_username_from_github_url(url):
    try:
        # remove query params
        url = url.split("?")[0]

        parts = url.strip("/").split("/")

        if "github.com" in parts:
            idx = parts.index("github.com")

            if len(parts) > idx + 1:
                username = parts[idx + 1]

                if username and username.lower() != "github.com":
                    return username
    except:
        pass

    return None


def normalize_github_username(github_field, links):
    # STEP 1: Extract from links FIRST (most reliable)
    for link in links:
        if "github.com" in link:
            username = extract_username_from_github_url(link)
            if username:
                return username

    # STEP 2: Fallback to LLM output
    if github_field:
        github_field = github_field.strip()

        # remove query params if present
        github_field = github_field.split("?")[0]

        # Case 1: full URL
        if "github.com" in github_field:
            username = extract_username_from_github_url(github_field)
            if username:
                return username

        # Case 2: plain username
        elif github_field.lower() != "github.com":
            return github_field

    return ""