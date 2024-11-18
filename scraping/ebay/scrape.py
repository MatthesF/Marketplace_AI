import requests
from bs4 import BeautifulSoup
import os
import json

def scrape_ebay_product(url):
    headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.ebay.com/",
    "Connection": "keep-alive"
    }

    
    # Send a GET request to the URL
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": f"Failed to fetch the page. Status code: {response.status_code}"}

    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")

    return soup

# Item specifics
def extract_item_specifics(soup):
    evo = soup.find_all("div", {"class": "ux-layout-section-evo__col"})

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
            # print(line.get_text())
            tmp.append(line.get_text())

        if len(tmp) > 1:

            data[tmp[0]] = tmp[1]


    return data


# Item description from the seller
def extract_seller_description(soup):
    soup.find("div", {"data-testid": "d-item-description"})#.get_text()

    # get src
    src  = soup.find("iframe", {"id": "desc_ifr"})["src"]

    # visit the src
    response = requests.get(src)
    response.text

    # parse the response
    soup2 = BeautifulSoup(response.text, "html.parser")

    # extract all the text
    # print(soup2.get_text().strip())

    return soup2.get_text().strip().replace("\n\n", "\n").replace("\n\n", "\n").replace("\n\n", "\n").replace("\n\n", "\n")


# Price
def extract_price(soup):
    # <div class="right-summary-panel-container vi-mast__col-right" id="RightSummaryPanel">
    return soup.find("div", {"id": "RightSummaryPanel"}).find_all("div", {"class" : 'x-price-primary'})[0].get_text()

# images
def get_image_urls(soup):

    srcs = []
    for line in soup.find_all("img",):
        if "src" in line.attrs:
            srcs.append(line["src"])
        elif "data-src" in line.attrs:
            srcs.append(line["data-src"])
        else:
            print(line)

    return srcs

# clean up urls
def clean_image_urls(image_urls):

    # remove duplicates
    uniques = set(image_urls)
    print(f"I found {len(image_urls)} images, with {len(uniques)} unique images")


    # check that they start with http
    valid = []
    for line in uniques:
        if not line.startswith("http"):
            print(line)
        else:
            valid.append(line)

    # check that they end with jpg or png
    images = []
    for line in valid:
        if not line.endswith("jpg") and not line.endswith("png"):
            print(line)
        else:
            images.append(line)

    print(f"I found {len(images)} valid images")
    return images

def download_image(src = "https://i.ebayimg.com/images/g/wCMAAOSwrcdnNvpw/s-l140.jpg", out_path="content/image.jpg"):
    # download an image
    
    response = requests.get(src)
    response.content

    with open(out_path, "wb") as f:
        f.write(response.content)

def download_images(image_urls, path='content'):
    for i, url in enumerate(image_urls):
        download_image(url, f"{path}/{i}.jpg")


def get_highest_folder_num(path='content'):
    # get highest number of folder
    return max([int(x.split("_")[0]) for x in os.listdir(path)])


def scrape(url):

    # Example usage
    loc = 'content'
    folder_num = get_highest_folder_num(loc) + 1


    soup = scrape_ebay_product(url)

    title = soup.find('span', {"class": "ux-textspans ux-textspans--BOLD"}).get_text()
    item_specifics = extract_item_specifics(soup)
    seller_description = extract_seller_description(soup)
    price = extract_price(soup)
    product_name = title.replace(" ", "_")[:20]

    data = {
        "title": title,
        **item_specifics,
        "seller_description": seller_description.encode("utf-8").decode("utf-8"),
        "price": price,
        "product_name": product_name,
        "url": url
    } 

    folder = f"{loc}/{folder_num}_{product_name}"
    os.makedirs(folder, exist_ok=True)

    with open(f"{folder}/data.json", "w") as f:
        json.dump(data, f)


    # download the images
    image_folder = f"{folder}/images"
    os.makedirs(image_folder, exist_ok=True)

    image_urls = get_image_urls(soup)
    image_urls = clean_image_urls(image_urls)
    download_images(image_urls, image_folder)

    print(f'Done with {title}, saved in {folder}')


if __name__ == "__main__":
    with open ("product_urls.txt", "r") as f:
        urls = f.readlines()

    prev_length = len(urls)

    urls = set(urls)  # remove duplicates

    if len(urls) != prev_length:
        print(f"Removed {prev_length - len(urls)} duplicates")

    for url in urls:
        scrape(url.strip())

