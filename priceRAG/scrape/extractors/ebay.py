import requests
from bs4 import BeautifulSoup
import os


class Ebayextractor:
    def __init__(self, url, output_path='content'):
        self.url = url
        self.output_path = output_path  # where to save data and images
        self.get_soup()
        self.get_title()

        if self.check_if_exists():
            raise ValueError(f"{self.product_name} already exists")

        self.get_description()
        self.get_price()
        self.get_attributes()
        self.get_image_links()

        self.concatenate_data_dict()

    def get_soup(self):

        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.ebay.com/",
        "Connection": "keep-alive"
        }

        # Send a GET request to the URL
        response = requests.get(self.url, headers=headers)
        if response.status_code != 200:
            return {"error": f"Failed to fetch the page. Status code: {response.status_code}"}

        # Parse the HTML content
        self.soup = BeautifulSoup(response.text, "html.parser")

    def get_title(self):
        self.title = self.soup.find('span', {"class": "ux-textspans ux-textspans--BOLD"}).get_text()
        self.product_name = self.title.replace(" ", "_")[:20].replace("/", "_").replace(',', '_').replace('__', '_')

    def check_if_exists(self):
        return any([self.product_name in x for x in os.listdir(self.output_path)])
    
    def get_description(self):
        src  = self.soup.find("iframe", {"id": "desc_ifr"})["src"]  # get src of the iframe
        response = requests.get(src)  # visit the src

        # parse the response
        soup2 = BeautifulSoup(response.text, "html.parser")

        self.desc = soup2.get_text().strip().replace("\n\n", "\n").replace("\n\n", "\n").replace("\n\n", "\n").replace("\n\n", "\n")

    def get_price(self):
        self.price = self.soup.find("div", {"id": "RightSummaryPanel"}).find_all("div", {"class" : 'x-price-primary'})[0].get_text()
         
    def get_attributes(self):
        evo = self.soup.find_all("div", {"class": "ux-layout-section-evo__col"})

        # tidy up the data, it currently looks like this:
        # [<span class="ux-textspans">Shoe Shaft Style</span>,
        #  <span class="ux-textspans">High Top</span>]

        # i want {"Shoe Shaft Style": "High Top"}

        # i can do this by iterating over the list and extracting the text from the span tags
        # then i can use the first element as the key and the second element as the value

        data = {}
        for line in evo:
            tmp = []
            for line in line.find_all("span", {"class" : "ux-textspans"}):
                tmp.append(line.get_text())

            if len(tmp) > 1:
                data[tmp[0]] = tmp[1]

        self.attributes = data
    
    def get_image_links(self):
        # Rough
        srcs = []
        for line in self.soup.find_all("img",):
            if "src" in line.attrs:
                srcs.append(line["src"])
            elif "data-src" in line.attrs:
                srcs.append(line["data-src"])
            else:
                pass

        # Fine
        ## remove duplicates
        uniques = set(srcs)


        ## check that they start with http
        valid = []
        for line in uniques:
            if line.startswith("http"):
                valid.append(line)

        # check that they end with jpg or png
        images = []
        for line in valid:
            if not line.endswith("jpg") and not line.endswith("png"):
                pass
            else:
                images.append(line)

    
        self.image_links = images

    def __repr__(self) -> str:
        return str({k : v[:12]+'...' for k, v in self.data.items()})
        
    def concatenate_data_dict(self):
        self.data = {
            "title": self.title,
            **self.attributes,
            "seller_description": self.desc.encode("utf-8").decode("utf-8"),
            "price": self.price,
            "product_name": self.product_name, 
            "url": self.url
        }

    
