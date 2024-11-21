# this should do a full update of the RAG databases
from scrape.utils import get_urls, extract, broken_images
from builder import VectorSearchBuild

# 1. run scraper
# 2. run builder

if __name__ == "__main__":
    # scrape the data

    history_path = 'priceRAG/scrape/history.csv'
    get_urls(history_path)   # parse history, getting the urls

    extract('dba')  # use request to get the images and texts from the urls
    extract('ebay')

    broken_images(base_path = 'priceRAG/scrape/content', delete=True, verbose=False)  # remove broken images

    # build the vectorstore
    v = VectorSearchBuild(base_path='priceRAG/scrape/content/',
                          sources=["dba", "ebay"]) 
    v.visualize_embeddings()
    v.save()


