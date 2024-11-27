# scraper_utils.py

import aiohttp
from bs4 import BeautifulSoup
import json
from config import PROXY_URL

# Async function to fetch the content of a page
async def fetch(url: str, session: aiohttp.ClientSession):
    async with session.get(url, proxy=PROXY_URL) as response:
        return await response.text()

# Function to extract categories from breadcrumb
async def get_categories(url: str, session: aiohttp.ClientSession):
    page_content = await fetch(url, session)
    soup = BeautifulSoup(page_content, 'html.parser')

    # Find the breadcrumb container
    breadcrumb_list = soup.find('ul', {'itemscope': '', 'itemtype': 'http://schema.org/BreadcrumbList'})
    
    # Extract all categories from the breadcrumb list
    categories = [li.find('span').text for li in breadcrumb_list.find_all('li') if li.find('span')]
    
    return categories

# Function to extract price, description, images, and product info from listing page
async def get_listing_details(url: str, session: aiohttp.ClientSession):
    page_content = await fetch(url, session)
    soup = BeautifulSoup(page_content, 'html.parser')

    # Extract price
    price_meta = soup.find('meta', {'property': 'product:price'})
    price = price_meta['content'] if price_meta else 'N/A'

    # Extract description
    description_meta = soup.find('meta', {'property': 'og:description'})
    description = description_meta['content'] if description_meta else 'N/A'

    # Extract main image(s) from <meta property="og:image">
    meta_images = [meta['content'] for meta in soup.find_all('meta', {'property': 'og:image'})]

    # Extract additional images from <img> tags
    img_tags = soup.find_all('img')
    img_urls = [img['src'] for img in img_tags if 'src' in img.attrs]

    # Combine all image URLs
    all_images = list(set(meta_images + img_urls))  # Use set to avoid duplicates

    # Extract product-specific info from the vip-matrix-data section
    product_info = {}
    vip_matrix_data = soup.find('div', class_='vip-matrix-data')
    if vip_matrix_data:
        dl = vip_matrix_data.find('dl')
        if dl:
            for dt in dl.find_all('dt'):
                key = dt.text.strip()
                dd = dt.find_next_sibling('dd')
                if dd:
                    value = dd.text.strip()
                    product_info[key] = value

    return {
        'price': price,
        'description': description,
        'images': all_images,
        'product_info': product_info,
        'url': url
    }

# Function to save data to JSON file
def save_data_to_json(scraped_data, filename="scraped_data.json"):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(scraped_data, f, ensure_ascii=False, indent=4)
        print(f"Data saved to {filename}")
