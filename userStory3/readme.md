# Book Data Scraper

Scrapes book data from [Books to Scrape](http://books.toscrape.com/) and exports it to `userStory3/output/books_data.csv`.

## Extracted Fields

- Title
- Price
- Rating
- Availability
- URL

## Run

```bash
/Users/pixel/userStories/.venv/bin/python -m userStory3.src.scraper.main
```

## Test

```bash
/Users/pixel/userStories/.venv/bin/python -m unittest userStory3.tests.test_scraper
```

The test command prints a coverage report after the tests finish.

If you are using a fresh environment, install the dependencies first:

```bash
python3 -m pip install -r userStory3/requirements.txt
```

## Error Handling

- Missing book fields are skipped and logged.
- HTTP and network errors are logged and handled without crashing the scraper.
- Pagination stops safely when a page cannot be fetched or no next link is available.
