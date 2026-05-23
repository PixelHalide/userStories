import os
import requests

FILE_URL = "https://drive.google.com/uc?id=1AWPf-pJodJKeHsARQK_RHiNsE8fjPCVK&export=download"

def download_file(url: str, attempts: int = 3) -> str:
    attemptCount = 0
    response = None
    while (attemptCount < attempts):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return response.text
            else:
                raise requests.RequestException(f"Failed to download file from {url}. Status code: {response.status_code}")
        except requests.RequestException as e:
            print(f"Attempt {attemptCount + 1} failed: {e}")
            attemptCount += 1
            if attemptCount >= attempts:
                raise requests.RequestException(f"Failed to download file from {url} after {attempts} attempts.")

    if response:
        with open("output.json", "wb") as file:
            file.write(response.content)