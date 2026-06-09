import logging
from pathlib import Path

from .scraper import OUTPUT_DIR, OUTPUT_FILE, scrape_to_csv


logging.basicConfig(
    filename="userStory3/scraper_errors.log",
    level=logging.INFO,
    format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
)


def main(output_dir: Path | str = OUTPUT_DIR, output_file: str = OUTPUT_FILE) -> Path:
    return scrape_to_csv(output_dir=output_dir, output_file=output_file)


if __name__ == "__main__":
    output_path = main()
    print(f"Saved book data to {output_path}")
