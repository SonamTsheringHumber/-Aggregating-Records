# TV Show Summary

This program downloads a page of TV show records from the public TVmaze API and summarizes them by genre, language, and premiere decade. It turns hundreds of raw, messy records into a small JSON report that is easy to read and compare.

## Data source

- URL: https://api.tvmaze.com/shows?page=0
- One record = one TV show (id, name, language, genres, premiered date, rating, network, and more).
- The page returns roughly 250 records. No account or API key is needed.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python records.py
```

The program writes `summary.json` in the current folder and prints a one-line confirmation. If the download fails it prints a short error message and exits without a traceback.

## Example output

Excerpt of `summary.json` (replace with a real excerpt from your own run):

```json
{
  "source_url": "https://api.tvmaze.com/shows?page=0",
  "records_processed": <number>,
  "shows_per_genre": { "Drama": <n>, "Comedy": <n>, ... },
  "average_rating_by_language": {
    "English": { "average_rating": <x.xx>, "rated_shows": <n> }
  },
  "shows_per_decade": { "1990s": <n>, "2000s": <n>, ... }
}
```

This tells you which genres dominate the page, how languages compare on average rating (with the number of rated shows behind each average), and which decades the shows come from.

## Data quirks

| Quirk found | What the program does |
|---|---|
| A show can have several genres | Genre counting loops over each show's genres, so a show counts once in every genre it has. |
| Some shows have no genres (empty list) | They are not counted under any genre and are reported in `missing_values.no_genre`. |
| Some shows have `rating.average` set to null | They are skipped when averaging, so they are not counted as a rating of 0. The number of rated shows is stored beside each average. |
| Some shows have no language | Their ratings are grouped under `"unknown"` rather than guessed. |
| Some shows have no premiere date, or a malformed one | They are left out of the decade counts and reported in `missing_values.no_premiere_date`. |
| Some shows have no network (web shows use `webChannel`) | A show is counted as missing only if both fields are empty. |
| Possible duplicate, non-dict, or id-less records | `clean_records` drops them and the number dropped is saved as `records_skipped`. |
| Network or HTTP failure, bad JSON | `fetch_records` raises a clear `DownloadError`; `main` prints it and exits with code 1. |

## Design choices

- **list**: holds the ordered records and the top-rated results, where order matters.
- **dict**: groups records by key (genre, language, decade) with fast lookup and easy JSON output.
- **set**: used for seen ids (fast duplicate check) and for each show's genres (so a repeated genre is counted once per show).
- **tuple**: `clean_records` returns a fixed `(records, skipped)` pair, and top-rated sorting uses `(rating, name)` pairs, which are small fixed-size, unchangeable groups.
- Each function does one job; aggregation functions only take records and return a result, so they can be tested with hand-made records and moved into a package next week unchanged.
- Comprehensions build the averages dict, the genre set, and the top-rated list.

## Known limitations

- Only page 0 is downloaded (about 250 shows); paging through the whole catalogue is not implemented.
- Ratings come from a single source and may be based on few votes.
- There are no automated tests yet (planned for Week 4).