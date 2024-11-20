from parse_history import get_urls
from extract import extract
from delete_bad_images import broken_images

if __name__ == '__main__':
    history_path = 'scrape/history.csv'
    get_urls(history_path)   # parse history, getting the urls

    # extract('dba')  # use request to get the images and texts from the urls
    # extract('ebay')

    broken_images(base_path = 'scrape/content', delete=True, verbose=False)

