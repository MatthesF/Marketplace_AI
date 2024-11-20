import pandas as pd

def get_urls(path = 'history.csv', verbose=True):
    df = pd.read_csv(path)

    # Check url
    df['ebay_in_url'] = df['url'].str.contains('https://www.ebay.com/itm', case=False)
    df['dba_in_url'] = df['url'].str.contains('dba', case=False)
    df['facebook_in_url'] = df['url'].str.contains('https://www.facebook.com/marketplace/item', case=False)

    # df[df['ebay_in_url']]['url'].unique()
    unique_item_urls_ebay = df[df['ebay_in_url']]['url'].unique()
    unique_item_urls_dba = df[df['dba_in_url']]['url'].unique()
    unique_item_urls_facebook = df[df['facebook_in_url']]['url'].unique()

    if verbose:
        print(f'We have {len(unique_item_urls_ebay)} unique items from ebay')
        print(f'We have {len(unique_item_urls_dba)} unique items from dba')
        print(f'We have {len(unique_item_urls_facebook)} unique items from Facebook Marketplace')

    # Save urls to txt files
    with open('scrape/content/urls_ebay.txt', 'w') as f:
        for item in unique_item_urls_ebay:
            f.write("%s\n" % item)
            
    with open('scrape/content/urls_dba.txt', 'w') as f:
        for item in unique_item_urls_dba:
            f.write("%s\n" % item)

    with open('scrape/content/urls_facebook.txt', 'w') as f:
        for item in unique_item_urls_facebook:
            f.write("%s\n" % item)

