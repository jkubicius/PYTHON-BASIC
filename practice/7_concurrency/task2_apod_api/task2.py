import os
import requests
import credentials
from concurrent.futures import ThreadPoolExecutor

API_KEY = credentials.API_KEY
APOD_ENDPOINT = "https://api.nasa.gov/planetary/apod"
OUTPUT_IMAGES = "./output_images"

def get_apod_metadata(start_date: str, end_date: str, api_key: str) -> list:
    params = {
        "api_key": api_key,
        "start_date": start_date,
        "end_date": end_date,
    }
    response = requests.get(APOD_ENDPOINT, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return []

def download_image(url: str):
    print(f"Downloading: {url}")
    response = requests.get(url)
    if response.status_code == 200:
        filename = url.split("/")[-1]
        filepath = os.path.join(OUTPUT_IMAGES, filename)
        with open(filepath, "wb") as f:
            f.write(response.content)

def download_apod_images(metadata: list):
    images = [d for d in metadata if d.get("media_type")=="image" and (d.get("hdurl") or d.get("url"))]
    print(f"Found {len(images)} images to download")

    os.makedirs(OUTPUT_IMAGES, exist_ok=True)

    with ThreadPoolExecutor(max_workers=5) as executor:
        urls = [d.get("hdurl") or d.get("url") for d in images]
        executor.map(download_image, urls)

def main():
    metadata = get_apod_metadata(
        start_date='2021-08-01',
        end_date='2021-09-30',
        api_key=API_KEY
    )
    download_apod_images(metadata)

if __name__ == '__main__':
    main()