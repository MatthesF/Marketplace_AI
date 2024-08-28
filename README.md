# Marketplace_AI

## preperation
* udemy course: https://www.udemy.com/course/langchain/learn/lecture/43404740#overview
* youtube course: https://www.youtube.com/playlist?list=PLfaIDFEXuae2LXbO1_PKyVJiQ23ZztA0x 

## Steps
0. user inputs:
    * currency
    * languages/ region
    * urgency
    * Tone of voice (formal, informal, consise, verbose)
    * API key
    * model selection
    * profile info: location mm.

1. the app recieves some images of an object for sale

> We want a JSON with the following fields:
* estimated price
* condition
* brand / manufacturer
* model
* product tags
* product category
* color if relevant
* do we have reciept?

2. What product is this?
3. Determine which fields in JSON are relevant for this item.
4. If information is missing, the app should ask for it. Maybe a chat interface?
5. Present toy listing to user, for confirmation.
6. Post through API to the server. 
    https://developers.facebook.com/docs/commerce-platform/platforms/distribution/MPApprovalAPI/
7. Iphone app
    * learn swift 

* For scraping: https://github.com/passivebot/facebook-marketplace-scraper/blob/main/app.py


## Research questions
* Should we give all pictures at once, or one by one?
* Should we finetune the model? What could we gain from this?
* To estimate price, should we: 1. have a database to look up in, 2. should we search online, or 3. should we use the base model to predict price? Does the price estimator need to be region aware? Is urgency relevant for price estimation?
* The app could ask for more pictures / or better pictures
* multi agent / single agent
* Is facebook marketplace the only relevant platform? Which platforms offer API POST?
* How to do A/B testing for each prompt?




## Implementation Strategy
* Build simple streamlit app, which has the following functionality:
    * Dropzone for images
    * Send images to model
    * recieve description of product in images
