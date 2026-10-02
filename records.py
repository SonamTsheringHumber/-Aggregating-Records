"""Summarize TV shows from the TVmaze public API.

Downloads one page of show records, cleans them, computes several
aggregations (shows per genre, average rating per language, shows per
decade, top rated shows, data-quality counts) and writes summary.json.
"""

import sys

import requests

SOURCE_URL = "https://api.tvmaze.com/shows?page=0"
TIMEOUT_SECONDS = 10
MIN_RECORDS = 50


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


def clean_records(raw_records):
    """Keep only usable show records.

    Drops entries that are not dicts, have no id, or repeat an id already
    seen. Returns a tuple (clean_records, skipped_count).
    """
    seen_ids = set()  
    clean = []
    for item in raw_records:
        if not isinstance(item, dict):
            continue
        show_id = item.get("id")
        if show_id is None or show_id in seen_ids:
            continue
        seen_ids.add(show_id)
        clean.append(item)
    return clean, len(raw_records) - len(clean)


def get_rating(show):
    """Return the show's average rating as a float, or None if unusable."""
    rating = show.get("rating")
    if not isinstance(rating, dict):
        return None
    value = rating.get("average")
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    if not 0 <= value <= 10:
        return None
    return float(value)


def get_language(show):
    """Return the show's language, or None if missing or blank."""
    language = show.get("language")
    if isinstance(language, str) and language.strip():
        return language.strip()
    return None


def get_premiere_year(show):
    """Return the premiere year as an int, or None if missing or malformed."""
    premiered = show.get("premiered")
    if not isinstance(premiered, str):
        return None
    try:
        year = int(premiered[:4])
    except ValueError:
        return None
    return year if 1850 <= year <= 2100 else None


def get_genres(show):
    """Return the set of clean genre names for a show (empty if none)."""
    genres = show.get("genres")
    if not isinstance(genres, list):
        return set()
    return {g.strip() for g in genres if isinstance(g, str) and g.strip()}


def main():
    """Download and clean the records, then report the counts."""
    try:
        raw_records = fetch_records(SOURCE_URL)
    except DownloadError as exc:
        sys.exit(f"Error: {exc}")
    records, skipped = clean_records(raw_records)
    if len(records) < MIN_RECORDS:
        sys.exit(f"Error: only {len(records)} usable records; need {MIN_RECORDS}.")
    print(f"Kept {len(records)} records, skipped {skipped}.")


if __name__ == "__main__":
    main()