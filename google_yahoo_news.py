import build_model, pickle
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import pickle
from alchemyapi import AlchemyAPI
import re
import datetime
from get_pickles import get_pickles
import os

model, vec, google_data, last_update = get_pickles()

def google_yahoo_news_updater():
    alchemyapi = AlchemyAPI()
    r = requests.get("http://news.google.com")
    soup = BeautifulSoup(r.text, "html.parser")
    divs = [div for div in soup.findAll('div', 'esc-lead-article-title-wrapper')]
    links = []
    bias_scores = []
    titles = []
    sentiments = []
    sentiment_scores = []
    sources = [source.text for source in soup.findAll('span', {'class': 'al-attribution-source'})]
    for div in divs:
        link = div.find_all('a', href=True)
        links.append(link[0]['href'])
        titles.append(link[0].findAll('span')[0].text)
    for link in links:
        response = alchemyapi.text('url', link)
        text = str(re.sub('[^\w\s]+', '', response['text']))
        text = str(re.sub('\n+', '', text)) 
        bias_scores.append(model.predict(vec.transform([text]).toarray())[0])

        #get sentiment
        response = alchemyapi.sentiment('url', link)
        if response.has_key('docSentiment'):
            print response['docSentiment'].get('type', 0) , response['docSentiment'].get('score', 0)
            sentiments.append(response['docSentiment']['type'])
            sentiment_scores.append(response['docSentiment'].get('score', 0))
    google_data = zip(titles, links, sources, bias_scores, sentiments, sentiment_scores)
    if os.getcwd().split('/')[1] != 'Users':
        my_dir = os.path.dirname(__file__)
        google_data_path = os.path.join(my_dir, 'pickles/google_data.pkl')
        last_update_path = os.path.join(my_dir, 'pickles/last_update.pkl')
        google_data = pickle.dump(google_data, open(google_data_path, "wb" ) )
        last_update  = pickle.dump(datetime.datetime.now(), open(last_update_path, "wb" ) )
    else:
        pickle.dump(google_data, open("pickles/google_data.pkl", "wb"))
        pickle.dump(datetime.datetime.now(), open("pickles/last_update.pkl", "wb"))

if __name__ == '__main__':
    google_yahoo_news_updater()