import re 
import tweepy 
from tweepy import OAuthHandler 
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from nltk.corpus import stopwords
from textblob import TextBlob
import pandas as pd
import numpy as np
from pymongo import MongoClient

client = MongoClient('localhost', 19823)
db = client.review
  
def clean_tweet(tweet): 
    return (' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())) 

def get_tweet_sentiment(tweet): 
    # create TextBlob object of passed tweet text 
    analysis = TextBlob(clean_tweet(tweet)) 
    # set sentiment 
    if analysis.sentiment.polarity > 0: 
        return 'positive'
    elif analysis.sentiment.polarity == 0: 
        return 'neutral'
    else: 
        return 'negative'

def sentiment_report(hash_id):
    t_count = db.tweet_sentiment.count({'hash_tag_id':hash_id})
    p_count = db.tweet_sentiment.count({'hash_tag_id':hash_id,'sentiment':'positive'})
    n_count = db.tweet_sentiment.count({'hash_tag_id':hash_id,'sentiment':'negative'})
    ne_count = db.tweet_sentiment.count({'hash_tag_id':hash_id,'sentiment':'neutral'})

    positive = 100*p_count/t_count
    negative = 100*n_count/t_count
    neutral = 100*ne_count/t_count

    return positive, negative, neutral

def cluster(p_id):
    df = pd.DataFrame(list(db.tmp_data.find({'process_id':p_id})))
    stop_words = stopwords.words('english')
    df1 = df.drop_duplicates()
    df1['tweet_c'] = df1['tweet'].str.replace('RT','')
    df1['tweet_c'] = df1['tweet'].apply(lambda x: " ".join(x.lower() for x in x.split() if x not in stop_words))
    df1['tweet_c'] = df1['tweet'].str.replace('[^\w\s]','')
    Vectorizer = TfidfVectorizer()
    x = Vectorizer.fit_transform(df1['tweet_c'])
    kmeans = KMeans(n_clusters= 2, random_state= 0)
    kmeans.fit(x)
    tweet = df1['tweet']
    tweet_type = kmeans.labels_
    tweet_id = df1['tweet_id']
    return tweet_type, tweet_id

def hashtags(p_id):
    a = ['Vijay', 'Sarkar']
    df = pd.DataFrame(list(db.tmp_data.find({'process_id':p_id})))
    df['hashtags_len'] = df['tweet'].apply(lambda x: len([x for x in x.split() if x.startswith('#')]))
    df['hashtags'] = df['tweet'].apply(lambda x: [x for x in x.split() if x !=[('#'+str(tag))for tag in a] and x.startswith('#')])
    hashtags = pd.Series(np.concatenate(df['hashtags']))
    trend_hashtags = hashtags.value_counts()
    trend = trend_hashtags.nlargest(10)
    
    return trend

def mentions():
    df = pd.DataFrame(list(db.tmp_data.find({'process_id':469})))
    df['Mentions'] = df['tweet'].apply(lambda x: [x for x in x.split() if not x.endswith(':') and x.startswith('@')])
    influential = pd.Series(np.concatenate(df['Mentions']))
    inf = influential.value_counts()
    print("Highest no of mentions",inf.nlargest(10))

def highest_rt():
    df = pd.DataFrame(list(db.tmp_data.find({'process_id':469})))
    print df['tweet'].value_counts().idxmax()

def influence():
    df = pd.DataFrame(list(db.tmp_data.find({'process_id':469})))
    df['influence'] = df['tweet'].apply(lambda x: [x for x in x.split() if x.endswith(':') and x.startswith('@')])
    influential = pd.Series(np.concatenate(df['influence']))
    inf = influential.value_counts()
    print("The most influential person is",inf.nlargest(10))

# def a():
#     a = 'vijay'
#     b = ('#'+str(a))
#     print b

# a()

# highest_rt()