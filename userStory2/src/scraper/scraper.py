import re
import logging
from pathlib import Path
import requests

FILE_URL = "https://drive.google.com/uc?id=1AWPf-pJodJKeHsARQK_RHiNsE8fjPCVK&export=download"
ALLOWED_FILE_TYPES = {"csv", "xls", "xlsx"}
OUTPUT_DIR = Path("output")

logger = logging.getLogger(__name__)


def identify_file_type_from_url(url: str) -> str | None:
    response = requests.head(url, allow_redirects=True, timeout=10)
    response.raise_for_status()

    filename_match = re.search(
        r'filename="?([^";]+)"?',
        response.headers.get("Content-Disposition", ""),
    )
    if not filename_match:
        return None

    file_type = filename_match.group(1).rsplit(".", 1)[-1].lower()
    return file_type if file_type in ALLOWED_FILE_TYPES else None


def download_file(url: str, output_dir: Path | str = OUTPUT_DIR, output_name: str = "download", attempts: int = 3):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for attempt in range(1, attempts + 1):
        try:
            file_type = identify_file_type_from_url(url)
            if not file_type:
                allowed = ", ".join(sorted(ALLOWED_FILE_TYPES))
                raise ValueError(f"Unsupported file type. Allowed file types: {allowed}.")

            output_path = output_dir / f"{output_name}.{file_type}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            with open(output_path, "wb") as file:
                file.write(response.content)

            return output_path
        except ValueError:
            logger.exception("Invalid file format for %s", url)
            raise
        except requests.RequestException as error:
            if attempt == attempts:
                message = f"Failed to download file from {url} after {attempts} attempts."
                logger.exception(message)
                raise requests.RequestException(
                    f"Failed to download file from {url} after {attempts} attempts."
                ) from error

            logger.warning("Attempt %s failed: %s", attempt, error)
