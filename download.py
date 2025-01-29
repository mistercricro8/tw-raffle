import asyncio
import csv
import os
import re
import time
from pathlib import Path
import requests
from playwright.async_api import async_playwright

START_URL = "nyenye"
A_CLASS = "css-175oi2r r-1pi2tsx r-1ny4l3l r-1loqt21"
IMG_CLASS = "css-9pa8cd"
BUTTON_CONTAINER_CLASS = "css-175oi2r r-1awozwy r-g2wdr4 r-16cnnyw r-1867qdf r-1phboty r-rs99b7 r-18u37iz r-1wtj0ep r-1mmae3n r-n7gxbd"
BUTTON_CLASS = "css-175oi2r r-sdzlij r-1phboty r-rs99b7 r-lrvibr r-faml9v r-2dysd3 r-15ysp7h r-4wgw6l r-3pj75a r-1loqt21 r-o7ynqc r-6416eg r-1ny4l3l"
CSV_FILE = "downloaded_images.csv"

Path("images").mkdir(exist_ok=True)

downloaded_images = set()
saved_users = set()


async def download_image(username, img_url):
    try:
        if "_normal.jpg" in img_url:
            return 

        img_folder = Path("images") / username
        img_folder.mkdir(exist_ok=True)

        img_name = img_url.split("/")[-1].split("?")[0] + ".png"
        img_path = img_folder / img_name

        if img_path.exists():
            return 

        response = requests.get(img_url, timeout=10)
        if response.status_code == 200:
            with open(img_path, "wb") as file:
                file.write(response.content)
            downloaded_images.add(img_url)

            if username not in saved_users:
                with open(CSV_FILE, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([username, img_url])
                saved_users.add(username)

            print(f"{img_url} -> {img_path}")
    except Exception as e:
        print(f"Error {img_url}: {e}")


async def extract_data(page):
    while True:
        try:
            elements = await page.query_selector_all(f"a.{A_CLASS.replace(' ', '.')}")
            for a_tag in elements:
                href = await a_tag.get_attribute("href")
                match = re.match(r"/([^/]+)/", href or "")
                if not match:
                    continue

                username = match.group(1)
                img_elements = await a_tag.query_selector_all(f"img.{IMG_CLASS.replace(' ', '.')}")
                for img in img_elements:
                    img_url = await img.get_attribute("src")
                    if img_url and img_url not in downloaded_images:
                        await download_image(username, img_url)

            button_container = await page.query_selector(f"div.{BUTTON_CONTAINER_CLASS.replace(' ', '.')}")
            if button_container:
                button = await button_container.query_selector(f"button.{BUTTON_CLASS.replace(' ', '.')}")
                if button:
                    print("loads more")
                    await button.click()
                    await asyncio.sleep(3)

            await page.evaluate("window.scrollBy(0, 500)")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"Error during extraction: {e}")
            break


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        await page.goto(START_URL)
        input("login...")
        await extract_data(page)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
