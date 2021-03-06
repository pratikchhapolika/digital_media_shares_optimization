import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup
import pymongo

def get_mashable_content(doc):

    """
    Pulls URL from mongoDB document and scrapes article title, article content
    and number of tags.  Stores results in MongoDB collection.

    Arguements:
    doc: MongoDB document containing mashable URL

    Output:
    Stores scraped data in MongoDB document
    """
    
    # request html data and create soup
    response = requests.get(doc['url'])
    
    if response.status_code == 200:

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # get article title
        try: 
            title = soup.find('h1', class_='title').text
        except:
            title = None
            
        # get article content
        try:
            content_list_temp = [text.text.encode('utf-8') 
                                 for text 
                                 in soup.find('section', 
                                 class_='article-content').find_all('p')]

            content = reduce(lambda x,y: x + ' ' + y, content_list_temp)
        except:
            content = None

        # get number of tags
        try:
            num_tags = len(soup.find('footer', 
                           class_='article-topics').find_all('a'))
        except:
            num_tags = None
            
    else:
        title = None
        content = None
        num_tags = None
        
    collection.update_one({"_id": doc["_id"]}, {"$set": {"title": title, 
                                                      "content": content,
                                                      "num_tags": num_tags}})

# connect to MongoDB collection
client = pymongo.MongoClient()
db = client.mashable
collection = client.mashable.articles

#define progress counter
progress_counter = 0 

# scrape mashable content for all URLs in collection
for doc in collection.find():

    get_mashable_content(doc)

    # show progress
    progress_counter += 1
    print progress_counter