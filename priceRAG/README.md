# Price Estimation

For price estimation, we have three ideas: _internet search_, _RAG_, _ask an LLM_.

| Method          | Basic idea                                                                         | Pros | Cons | Comments |
| --------------- | ---------------------------------------------------------------------------------- | ---- | ---- | -------- |
| Internet search | Can we just search google to get an approximate price, or at least an upper bound? |      |      |          |
| RAG             |                                                                                    |      |      |          |
| Ask LLM         |                                                                                    |      |      |          |

## RAG

To build a RAG-based price estimator, we need to:

- Scrape second hand platforms
- Clean up scraped data
- build RAG databases
- Perform look up in database

#### Open questions

- How many products do we need for an effective RAG-based price predictor?
- What to do when we get multiple matches from RAG inference?

### Scraping

Initial results indicate that Ebay and DBA are accessible, but that FaceBookMarketPlace is not.

- The way I scrape, is to visit pages in chrome, and then download the history. This approach is only appropriate for <1,000 items.
- All images from the page are downloaded
- specific text fields are extracted and saved.

## Cleaning

We obtain many irrelevant images, for example page logo, dublicates with different sizes, images of other products. The order we

1. Check if file can be opened
   1. using `PIL.Image.open` we get an error if its a faulty image
2. Identify duplicates
   1. Identify repeated aspect ratios
   2. Downscale images and compare pixel values
3. Which images are actually of the product?
   - Look for outlier in CLIP embedding
   - Ask LLM

## RAG databases

Should we use an image based vector database, or one based on text? Lets implement both!

- images database
- text database

## Inference

- `img`-`img`
- `img`-`txt`
- `txt`-`img`
- `txt`-`txt`

## Validation

#TODO
