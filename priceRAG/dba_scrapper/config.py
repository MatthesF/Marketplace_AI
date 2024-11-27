# Proxy settings
PROXY_USERNAME = 'sp7odyv3im'
PROXY_PASSWORD = 'kuJtM0~7Eg1Rh8ddap'
PROXY_URL = f"http://{PROXY_USERNAME}:{PROXY_PASSWORD}@gate.smartproxy.com:7000"

# Main URL for the listings (can be adjusted to the website being scraped)
BASE_URL = "https://www.dba.dk/soeg/side-{}"  # The placeholder {} will be replaced by page number

# Page range to scrape
START_PAGE = 2
END_PAGE = 101

# Output file for scraped data
OUTPUT_FILE = 'scraped_data.json'
