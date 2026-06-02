import logging
from . import mapper
from . import scraper


logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")


def main():
    file_path = scraper.download_file(scraper.FILE_URL)
    data = mapper.map_data(file_path)
    return data


if __name__ == "__main__":
    main()
