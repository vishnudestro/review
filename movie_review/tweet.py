import multiprocessing
from tweepy import Stream
from tweepy import OAuthHandler
from textblob import TextBlob
from steaming import SteamListener, Steam
import time
import json
import os
import pymongo
import tweet_analysis as ta
from mongothon import Schema, create_model
from db_schema import tmp_process_schema, tmp_data_schema, tweet_sentiment_schema
from pymongo import MongoClient

client = MongoClient('localhost', 19823)
db = client.review

Tmp = create_model(tmp_process_schema, db['tmp_process'])
Tmp_data = create_model(tmp_data_schema, db['tmp_data'])
Tweet = create_model(tweet_sentiment_schema, db['tweet_sentiment'])

consumer_key = 'QSN9oHHEm5ezPd9zO3IkLT0Iw'
consumer_secret = 'ugzpMUZqFkkYuTdSNem0DXCwTdIGuKlDXDcPYBoC4DT2DW2H2b'
access_token = '4495885394-mhGC0hDEqxm1fupzRt7daLqWXLRpKzD5xjwUbhL'
access_secret = 't1gB4ISR96ga0NFgd7zYHSjBQXugq3vuoAqHhxfoJBpD8'

class Myclass():
    def __init__(self, tag, h_id, u_id, m_id):
        self.tag = tag
        self.h_id = h_id
        self.u_id = u_id
        self.m_id = m_id

    def myfunc(self):
        tag = self.tag
        h_id = self.h_id
        u_id = self.u_id
        m_id = self.m_id
        return tag, h_id, u_id, m_id

    def myfunc1(self):
        l = listener()
        l.test(self.tag, self.h_id, self.u_id, self.m_id)

class listener(SteamListener):
    try:
        def process(self, tag, h_id):
            try:
                auth = OAuthHandler(consumer_key, consumer_secret)
                auth.set_access_token(access_token, access_secret)
                twitterStream = Steam(auth, listener())
                print("process start")
                twitterStream.filter(track = tag, hash_id = h_id, stall_warnings = True)
            except Exception as e:
                print ('Error in process: %s' % str(e))

        def test(self, tag, h_id, u_id, m_id):
            try:
                self.tag = tag
                self.h_id = h_id
                self.u_id = u_id
                self.m_id = m_id
                process_jobs = [] 
                pro = multiprocessing.Process(target = self.process, args = (self.tag, self.h_id))
                process_jobs.append(pro)
                pro.start()
                self.process_id = pro.pid
                
                #Process details
                tmp_pro_data = Tmp({'movie_id':self.m_id,'process_id':self.process_id,'user_id':self.u_id,'hash_tag_id':str(self.h_id),'hash_tags':self.tag,'process_status':True})
                tmp_pro_data.save()
                return self.process_id
            
            except Exception as e:
                print ('Error in test: %s' % str(e))   
        
        def on_data(self,data,hash_id):
            try:
                h ={}
                a = json.loads(data)
                print 'collecting'
                tmp = db.tmp_process.find({'hash_tag_id':str(hash_id),'process_status':True})
                for each in tmp:
                    #Process data details
                    tmp_data = Tmp_data({'process_id':each['process_id'],'user_id':each['user_id'],'hash_tag_id':str(hash_id),
                    'created_at':str(a['created_at']), 'tweet_id':a['id'], 'tweet':a['text']})
                    tmp_data.save()
                    
                    #Sentiment Analysis for each tweet
                    sentiment = self.sentiment(a['text'])
                    twt_sent = Tweet({'user_id':each['user_id'],'process_id':each['process_id'],'hash_tag_id':str(hash_id), 'movie_id':each['movie_id'],'tweet':a['text'],'sentiment':sentiment})
                    twt_sent.save()   
            except BaseException as e:
                print('Error on_data: %s' % str(e))
            return "Sucess" 
        
        def sentiment(tweet):
            tweets = (' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split()))
            # create TextBlob object of passed tweet text
            analysis = TextBlob(tweets)
            # set sentiment
            if analysis.sentiment.polarity > 0:
                return 'positive'
            elif analysis.sentiment.polarity == 0:
                return 'neutral'
            else:
                return 'negative' 
    
    except Exception as e:
        print ('error in class: %s' % str(e))