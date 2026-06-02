import logging
import tempfile
from pathlib import Path

from . import mapper
from . import scraper


logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")


def main(output_dir: Path | str = scraper.OUTPUT_DIR, output_name: str = "download"):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = scraper.download_file(scraper.FILE_URL, output_dir=temp_dir, output_name=output_name)
        data = mapper.map_data(file_path)

    output_path = output_dir / f"{output_name}.csv"
    data.to_csv(output_path, index=False)

    return data


if __name__ == "__main__":
    main()
