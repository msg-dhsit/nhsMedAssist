"""Central definition for NICE-related URLs and labels used across the app."""

from __future__ import annotations

from urllib.parse import quote_plus, urljoin

# Base search template for NICE guidance (expects a formatted query string).
_SEARCH_TEMPLATE = (
    "https://www.nice.org.uk/search?"
    "ndt=Guidance&rt=Guidance&q={query}"
)

# Root domain for NICE content.
NICE_BASE_URL = "https://www.nice.org.uk"

# Default symptom keyword leveraged by NICE extraction logic.
DEFAULT_SYMPTOM = "hypertension"

# Canonical guidance heading consumed by the UI.
PRIMARY_GUIDANCE_KEY = "Hypertension in adults: diagnosis and management"


def build_search_url(query: str) -> str:
    """
    Construct a NICE search URL for the supplied query, performing URL encoding.
    """
    if not query or not query.strip():
        raise ValueError("NICE search query must be a non-empty string.")
    encoded_query = quote_plus(query.strip())
    return _SEARCH_TEMPLATE.format(query=encoded_query)


class _SearchUrl(str):
    """
    Backwards compatible proxy so legacy `.format(symptom)` calls continue working.
    """

    def format(self, query: str) -> str:  # type: ignore[override]
        return build_search_url(query)


# Expose the proxy instance under the original attribute name expected by consumers.
searchUrl: _SearchUrl = _SearchUrl(_SEARCH_TEMPLATE)


def ensure_absolute(url: str | None) -> str:
    """Guarantee that NICE URLs are absolute."""
    if not url:
        return NICE_BASE_URL
    return url if url.startswith("http") else urljoin(NICE_BASE_URL, url)


__all__ = [
    "DEFAULT_SYMPTOM",
    "NICE_BASE_URL",
    "PRIMARY_GUIDANCE_KEY",
    "build_search_url",
    "ensure_absolute",
    "searchUrl",
]
