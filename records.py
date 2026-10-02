"""Summarize TV shows from the TVmaze public API.

Downloads one page of show records, cleans them, computes several
aggregations (shows per genre, average rating per language, shows per
decade, top rated shows, data-quality counts) and writes summary.json.
"""

import sys

import requests

SOURCE_URL = "https://api.tvmaze.com/shows?page=0"
TIMEOUT_SECONDS = 10


class DownloadError(Exception):
    """Raised when the records cannot be downloaded or understood."""

def fetch_records(url):
    """Download the records from url and return them as a list of dicts.

    Raises DownloadError with a readable message on any network, HTTP or
    JSON problem.
    """
    try:
        response = requests.get(url, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.Timeout as exc:
        raise DownloadError(
            f"The request to {url} timed out after {TIMEOUT_SECONDS} seconds."
        ) from exc
    except requests.exceptions.ConnectionError as exc:
        raise DownloadError(
            f"Could not connect to {url}. Check your internet connection."
        ) from exc
    except requests.exceptions.HTTPError as exc:
        raise DownloadError(f"The server returned an error: {exc}") from exc
    except (requests.exceptions.RequestException, ValueError) as exc:
        raise DownloadError(f"Could not read the response from {url}: {exc}") from exc

    if not isinstance(data, list):
        raise DownloadError("Unexpected response format: expected a list of shows.")
    return data


def main():
    """Download the records and print how many came back."""
    try:
        raw_records = fetch_records(SOURCE_URL)
    except DownloadError as exc:
        sys.exit(f"Error: {exc}")
    print(f"Downloaded {len(raw_records)} records.")


if __name__ == "__main__":
    main()