import requests
import os
import json
import argparse

from scrape.extractors import DBAextractor, Ebayextractor

# helper functions
def get_highest_folder_num(path='content'):
    # get highest number of folder
    try:
        return max([int(x.split("_")[0]) for x in os.listdir(path)])
    except:
        os.makedirs(path, exist_ok=True)
        return 0

def download_image(src, out_path="content/image.jpg"):
    # download an image
    
    response = requests.get(src)
    response.content

    with open(out_path, "wb") as f:
        f.write(response.content)

def download_images(image_urls, path='content'):
    for i, url in enumerate(image_urls):
        download_image(url, f"{path}/{i}.jpg")

def get_urls(path='urls.txt'):
    with open(path, 'r') as f:
        urls = f.readlines()
        num_urls = len(urls)
        # urls = [url.strip() for url in urls if 'id' in url]
        # if len(urls) != num_urls:
        #     print(f"Skipping {num_urls - len(urls)} invalid url/s")
    return urls

# check if dba.product_name already exists in folder
def check_if_exists(product_name, path='content'):
    return any([product_name in x for x in os.listdir(path)])


def extract(source):
    url_path = f'priceRAG/scrape/content/urls_{source}.txt'
    extractor = {
        'ebay' : Ebayextractor,
        'dba' : DBAextractor
    }[source]


    loc = f"priceRAG/scrape/content/{source}"
    folder_num = get_highest_folder_num(loc) + 1
    urls = get_urls(url_path)

    print('\nStaring extraction...')
    for i, url in enumerate(urls):
        try:
            dba = extractor(url, output_path=loc)
            
            folder = f"{loc}/{folder_num}_{dba.product_name}"
            os.makedirs(folder, exist_ok=True)

            with open(f"{folder}/data.json", "w") as f:
                json.dump(dba.data, f)

            # download the images
            image_folder = f"{folder}/images"
            os.makedirs(image_folder, exist_ok=True)

            download_images(dba.image_links, image_folder)

            print(f'--- Done with[{i} / {len(urls)}]: {dba}')

            folder_num += 1
    
        except Exception as e:
            print(f"{e}\t url: {url.strip()[:50] + '...' if len(url) > 50 else url.strip()}")
            continue

