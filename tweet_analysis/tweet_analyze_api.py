from flask import Flask
from pymongo import MongoClient
from flask import jsonify,request
from flask import render_template
from textblob import TextBlob 
import pandas as pd 
import numpy as np
import re
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans 
from nltk.corpus import stopwords

client = MongoClient('localhost', 19823)
db = client.review
app = Flask(__name__)

@app.route('/influence')
def influential_user():
    tag = []
    t_data = request.args.get('tags')
    tags = [eacht.strip() for eacht in t_data.split(',')]
    pro_id = request.args.get("pro_id")
    #Creating a Data frame for analysis
    df = pd.DataFrame(list(db.tmp_data.find({'process_id':int(pro_id)})))
    #Finding Most Influential Person
    influence = df['tweet'].apply(lambda x: [x for x in x.split() if x.startswith('@') and x.endswith(':')])   
    influential = pd.Series(np.concatenate(influence))
    inf = (influential.value_counts()).to_string()
    #Highest RT 
    RT = df['tweet'].value_counts().idxmax()
    #Who are the people mentioned in the collected tweet 
    Mentions_1 = df['tweet'].apply(lambda x: [x for x in x.split() if not x.endswith(':') and x.startswith('@') and len(x) > 1])
    mentions = pd.Series(np.concatenate(Mentions_1))
    ment = mentions.value_counts()
    ment_l = ment.nlargest(10)
    ment_str = ment_l.to_string()
    #No of hashtags in the collected tweets 
    hashtags_len = df['tweet'].apply(lambda x: len([x for x in x.split() if x.startswith('#')]))
    #Trending Hashtags excluding the input
    hashtags = df['tweet'].apply(lambda x: [x for x in x.split() if x != [('#'+str(tag))for tag in tags] and x.startswith('#')])
    hashtags = pd.Series(np.concatenate(hashtags))
    trend_hashtags = hashtags.value_counts()
    ths_lar = trend_hashtags.nlargest(10)
    ths_str = ths_lar.to_string()
    
    #Creating a json file to return  
    json_data = {
        'Highest RT' : RT,
        'Influential' :data_split(inf),
        'Mentions' : data_split(ment_str),
        'Trending Hashtags' : data_split(ths_str)
    }
    return jsonify(json_data)

def data_split(data):
        data_count = []
        split_data = [each.strip() for each in data.split('\n')]
        for i in split_data:
            split_empty = i.split(' ')
            filter_data = filter(None, split_empty)
            if filter_data[0].startswith('#'):
                value = {
                    'hash_tag':filter_data[0],
                    'count':int(filter_data[1])
                }
            else:
                value = {
                'mentions':filter_data[0],
                'count':int(filter_data[1])
                }
            data_count.append(value)
            
        return data_count
    
@app.route('/cluster')
def Clustering():
    pro_id = request.args.get("pro_id")
    df = pd.DataFrame(list(db.tmp_data.find({'process_id':int(pro_id)})))
    stop_words = stopwords.words('english')
    df1 = df.drop_duplicates()
    df1['tweet_c'] = df1['tweet'].str.replace('RT','')
    df1['tweet_c'] = df1['tweet'].apply(lambda x: " ".join(x.lower() for x in x.split() if x not in stop_words))
    df1['tweet_c'] = df1['tweet'].str.replace('[^\w\s]','')
    Vectorizer = TfidfVectorizer()
    x = Vectorizer.fit_transform(df1['tweet_c'])
    kmeans = KMeans(n_clusters= 2, random_state= 0)
    kmeans.fit(x)
    clusster_map = pd.DataFrame()
    clusster_map['data_index'] = df1['tweet']
    clusster_map['cluster'] = kmeans.labels_
    clusster_map['tweet_id'] = df1['tweet_id']
    json = clusster_map.to_json(orient= 'split')
    return (json)

@app.route('/sentiment')
def get_tweet_sentiment():
    pro_id = request.args.get("pro_id")
    hash_tag_id = request.args.get('hash_tag_id')
    t_count = db.tweet_sentiment.count({'process_id':int(pro_id)})
    p_count = db.tweet_sentiment.count({'process_id':int(pro_id),'sentiment':'positive'})
    n_count = db.tweet_sentiment.count({'process_id':int(pro_id),'sentiment':'negative'})
    ne_count = db.tweet_sentiment.count({'process_id':int(pro_id),'sentiment':'neutral'})
    return jsonify(
    positive = 100*p_count/t_count,
    negative = 100*n_count/t_count,
    neutral = 100*ne_count/t_count)

@app.route('/wordcloud')
def wordcloud():
    pro_id = request.args.get("pro_id")
    df = pd.DataFrame(list(db.tmp_data.find({'process_id':int(pro_id)})))
    keywords = df['tweet'].str.split()
    words= pd.Series(np.concatenate(keywords))
    words.value_counts()

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 8000, debug = True)