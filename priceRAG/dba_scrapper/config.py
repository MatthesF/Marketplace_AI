from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Proxy settings
PROXY_USERNAME = os.getenv('PROXY_USERNAME')
PROXY_PASSWORD = os.getenv('PROXY_PASSWORD')
PROXY_URL = f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@gate.smartproxy.com:7000"

# Main URL for the listings (can be adjusted to the website being scraped)
BASE_URL = "https://www.dba.dk/soeg/side-{}"  # The placeholder {} will be replaced by page number

# Page range to scrape
START_PAGE = 2
END_PAGE = 101

OUTPUT_FILE = 'scraped_data.json'

# Rate-limiting setting (seconds)
REQUEST_DELAY = 2  # Adjust this to control rate-limiting