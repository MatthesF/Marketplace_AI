from utils import get_urls, extract, broken_images

if __name__ == '__main__':
    history_path = 'scrape/history.csv'
    get_urls(history_path)   # parse history, getting the urls

    extract('dba')  # use request to get the images and texts from the urls
    extract('ebay')

    broken_images(base_path = 'scrape/content', delete=True, verbose=False)

