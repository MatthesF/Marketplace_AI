import asyncio
import aiohttp
from scraper_utils import get_categories, get_listing_details, save_data_to_json, fetch
from config import BASE_URL, START_PAGE, END_PAGE, REQUEST_DELAY
import time
import hashlib
from bs4 import BeautifulSoup

# Async function to scrape data from a single page
async def scrape_page(page_number: int, session: aiohttp.ClientSession):
    main_url = BASE_URL.format(page_number)

    # Fetch the main page content
    page_content = await fetch(main_url, session)
    if not page_content:
        return []

    soup = BeautifulSoup(page_content, 'html.parser')

    # Find all listing links (assuming they have the class "listingLink")
    listing_links = soup.find_all('a', class_='listingLink')

    # List to store scraped data for this page
    page_data = []

    # Loop through all the listing links and scrape data
    for link in listing_links:
        listing_url = link['href']
        print(f"Scraping {listing_url}...")

        # Get detailed information for the listing
        listing_details = await get_listing_details(listing_url, session)

        # Store the extracted information
        if listing_details:
            page_data.append(listing_details)
        
        # Rate limiting
        await asyncio.sleep(REQUEST_DELAY)

    return page_data


# Main async function to manage the whole scraping process
async def main():
    async with aiohttp.ClientSession() as session:
        all_data = []
        unique_urls = set()

        # Loop through pages from START_PAGE to END_PAGE
        for page_number in range(START_PAGE, END_PAGE + 1):
            print(f"Scraping page {page_number}...")
            start_time = time.time()
            page_data = await scrape_page(page_number, session)

            # Remove duplicates based on URL
            for item in page_data:
                url_hash = hashlib.md5(item['url'].encode()).hexdigest()
                if url_hash not in unique_urls:
                    unique_urls.add(url_hash)
                    all_data.append(item)

            end_time = time.time()
            print(f"Time taken to scrape page {page_number}: {end_time - start_time:.2f} seconds")

        # Save the data to JSON
        save_data_to_json(all_data)


if __name__ == '__main__':
    asyncio.run(main())
