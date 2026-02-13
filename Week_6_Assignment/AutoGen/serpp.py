import os
import sys
import time
from typing import List, Tuple, Optional
import requests
from urllib.parse import quote_plus
from dotenv import load_dotenv


class SerpApiError(RuntimeError):
    """Raised for SerpAPI configuration or response issues."""


def _get_env_key(name: str) -> str:
    """Fetch an env var and raise a clear error if missing."""
    val = os.getenv(name)
    if not val:
        raise SerpApiError(
            f"{name} is not set. Create a .env file with:\n\n"
            f"    {name}=your_value_here\n\n"
            "and/or export it in your shell."
        )
    return val


def search_serpapi(
    query: str,
    *,
    limit: int = 10,
    engine: str = "bing",  # "bing" (default) or "google"
    serpapi_key: Optional[str] = None,
    timeout_s: float = 30.0,
    retries: int = 2,
    backoff_sec: float = 2.0,
) -> Tuple[List[str], str]:
    """
    Search via SerpAPI and return:
      - list of SERP result links (deduped, up to `limit`)
      - google-style search link (e.g., https://www.google.com/search?q=virat+kohli)

    Parameters
    ----------
    query : str
        Your search query
    limit : int
        Max results to return (default 10)
    engine : str
        "bing" (default) or "google"
    serpapi_key : Optional[str]
        If provided, overrides the key loaded from environment (.env)
    timeout_s : float
        Request timeout in seconds
    retries : int
        Number of retry attempts on transient HTTP/network errors
    backoff_sec : float
        Backoff time between retries
    """
    load_dotenv()
    api_key = serpapi_key or _get_env_key("SERPAPI_KEY")

    # Build a google-style link for convenience/preview
    google_style_link = f"https://www.google.com/search?q={quote_plus(query)}"

    params = {
        "q": query,
        "api_key": api_key,
        "num": limit,
        "engine": engine,  # "bing" or "google"
    }

    last_exc: Optional[Exception] = None
    for attempt in range(1, retries + 2):  # e.g., retries=2 -> attempts = 3
        try:
            resp = requests.get(
                "https://serpapi.com/search",
                params=params,
                timeout=timeout_s,
            )
            # Raise for HTTP 4xx/5xx
            resp.raise_for_status()
            data = resp.json()

            # SerpAPI errors come in JSON sometimes even with 200 status
            if "error" in data:
                raise SerpApiError(f"SerpAPI error: {data.get('error')}")

            # Extract links from the payload
            links: List[str] = []
            for item in data.get("organic_results", []) or []:
                link = item.get("link")
                if link:
                    links.append(link)

            # Deduplicate while preserving order
            seen = set()
            deduped = []
            for l in links:
                if l not in seen:
                    seen.add(l)
                    deduped.append(l)

            return deduped[:limit], google_style_link

        except (requests.Timeout, requests.ConnectionError) as e:
            last_exc = e
            if attempt <= retries:
                time.sleep(backoff_sec * attempt)
                continue
            raise SerpApiError(
                f"Network error after {attempt} attempt(s): {e}"
            ) from e
        except requests.HTTPError as e:
            # For 4xx/5xx, don’t retry if it’s likely a bad request/invalid key
            status = getattr(e.response, "status_code", None)
            detail = e.response.text if getattr(e, "response", None) else str(e)
            # Retry only on transient 5xx
            if status and 500 <= status < 600 and attempt <= retries:
                last_exc = e
                time.sleep(backoff_sec * attempt)
                continue
            raise SerpApiError(
                f"HTTP error {status or ''} from SerpAPI: {detail}"
            ) from e
        except ValueError as e:
            # JSON parse errors
            raise SerpApiError(f"Invalid JSON from SerpAPI: {e}") from e
        except Exception as e:
            # Any unexpected errors
            raise SerpApiError(f"Unexpected error: {e}") from e

    # Exhausted retries (should not get here due to returns/raises above)
    if last_exc:
        raise SerpApiError(f"Exhausted retries: {last_exc}")
    raise SerpApiError("Exhausted retries with unknown error.")


# -----------------------------
# Example CLI usage
# -----------------------------
if __name__ == "__main__":
    try:
        query = sys.argv[1] if len(sys.argv) > 1 else "Karan Krishna"
        links, google_link = search_serpapi(query, limit=10, engine="bing")
        print("🔗 Google‑style search link:")
        print(google_link)

        print("\n🔗 SERP results:")
        for l in links:
            print("-", l)
    except SerpApiError as e:
        print(f"[SerpApiError] {e}", file=sys.stderr)
        sys.exit(1)