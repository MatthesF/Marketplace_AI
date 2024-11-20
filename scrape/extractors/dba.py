import requests
from bs4 import BeautifulSoup
import re
import os


class DBAextractor:
    def __init__(self, url, output_path='content', verbose=False):
        self.url = url.strip()
        self.output_path = output_path
        self.verbose = verbose
        self.get_soup()
        self.get_title()

        if self.check_if_exists():
            raise ValueError(f"{self.product_name} already exists")
        
        self.get_description()
        self.get_price()
        self.get_attributes()
        self.get_image_links()

        self.concatenate_data_dict()

    # def get_soup(self):
    #     response = requests.get(self.url)
    #     self.soup = BeautifulSoup(response.text, 'html.parser')
    def get_soup(self):

        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.dba.dk/",
        "Connection": "keep-alive"
        }

        # Send a GET request to the URL
        response = requests.get(self.url, headers=headers)
        if response.status_code != 200:
            print('response.status_code:', response.status_code)
            print('url:', self.url)
            print('response.reason:', response.reason)
            print('response.text:', response.text)


            return {"error": f"Failed to fetch the page. Status code: {response.status_code}"}

        # Parse the HTML content
        self.soup = BeautifulSoup(response.text, "html.parser")
    def get_title(self):
        self.title = self.soup.find_all('title')[0].text.split(' - ')[0]
        self.product_name = self.title.replace(" ", "_")[:20].replace("/", "_").replace(',', '_').replace('__', '_')
        if self.verbose:
            print(f"Title: {self.title}")
            print(f"Product name: {self.product_name}")

    def check_if_exists(self):
        return any([self.product_name in x for x in os.listdir(self.output_path)])

    def get_description(self):
        meta_desc = self.soup.find_all('meta', {'name': 'description'})
        self.desc = meta_desc[0]['content'].strip()
        
    def get_price(self):
        self.price = self.soup.find_all('meta', {'property': 'product:price'})[0]['content']
    
    def get_attributes(self):
        vmd = self.soup.find_all('div', {'class': 'vip-matrix-data'})
        dt = vmd[0].find_all('dt')
        dd = vmd[0].find_all('dd')
        labels = [d.text for d in dt]
        values = [d.text for d in dd]
        self.attributes = dict(zip(labels, values))
    
    def get_image_links(self):
        scripts = self.soup.find_all('script')
        regex = 'https://billeder.dba.dk/dba/[a-z0-9-]*.jpeg[?]'
        links = []
        for script in scripts:
            for link in re.findall(regex, str(script)):
                links.append(link)
        links = list(set(links))
        self.image_links = links

    def __repr__(self) -> str:
        # for k,v in self.data.items():
        #     print(f"{k}: {v}, {type(v)}")
        return str({k : v[:12]+'...' for k, v in self.data.items()})
        return f"Title: {self.title}\n\nDescription: {self.desc}\n\nPrice: {self.price}\n\nAttributes: {self.attributes}\n\nNumber of images: {len(self.image_links)}"

    def concatenate_data_dict(self):
        self.data = {
            "title": self.title,
            **self.attributes,
            "seller_description": self.desc.encode("utf-8").decode("utf-8"),
            "price": self.price,
            "product_name": self.product_name, 
            "url": self.url
        }
