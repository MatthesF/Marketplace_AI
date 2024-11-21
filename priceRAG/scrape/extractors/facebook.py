url = 'https://www.facebook.com/marketplace/item/562357142845449/?ref=browse_tab&referral_code=marketplace_top_picks&referral_story_type=top_picks'

import requests
from bs4 import BeautifulSoup

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

print(soup.find_all('meta'))