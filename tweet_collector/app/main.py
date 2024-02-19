import multiprocessing
from tweepy import Stream
from tweepy import OAuthHandler
from textblob import TextBlob
from steaming import SteamListener, Steam
import time
import json
import os
from flask import Flask, request, render_template, jsonify, Response
import pymongo
from mongothon import Schema, create_model
from db_schema import tmp_process_schema, tmp_data_schema, tweet_sentiment_schema, tweet_user_schema
from pymongo import MongoClient
import re

app = Flask(__name__)

client = MongoClient('mongo', 19823)
db = client.user_data

Tmp = create_model(tmp_process_schema, db['tmp_process'])
Tmp_data = create_model(tmp_data_schema, db['tmp_data'])
Tweet = create_model(tweet_sentiment_schema, db['tweet_sentiment'])
Tweet_user = create_model(tweet_user_schema,db['tweet_user'])

consumer_key = 'QSN9oHHEm5ezPd9zO3IkLT0Iw'
consumer_secret = 'ugzpMUZqFkkYuTdSNem0DXCwTdIGuKlDXDcPYBoC4DT2DW2H2b'
access_token = '4495885394-mhGC0hDEqxm1fupzRt7daLqWXLRpKzD5xjwUbhL'
access_secret = 't1gB4ISR96ga0NFgd7zYHSjBQXugq3vuoAqHhxfoJBpD8'

@app.route('/')
def hello():
    return 'Movie review'

class Myclass():
    @app.route('/start')
    def start():
        tag =[]
        t_data = request.args.get('hash_tag')
        tag = [eacht.strip() for eacht in t_data.split(',')]
        h_id = request.args.get('hash_tag_id')
        u_id = request.args.get('user_id')
        m_id = request.args.get('movie_id')
        l = listener()
        process_id = l.test(tag, h_id, u_id, m_id)
        if process_id != None:
            return jsonify(process_id=process_id, tags=tag, status=True)
        else:
            return jsonify(process_id=process_id, tags=tag, status=False)

    @app.route('/stop')
    def stop():
        process_id = request.args.get('process_id')
        hash_tag_id = request.args.get('hash_tag_id')
        kill_value = os.system("kill -9 "+str(process_id))
        if kill_value == 0:
            return jsonify(process_id=int(process_id), hash_tag_id =str(hash_tag_id), status=True)   
        else:
            return jsonify(process_id=int(process_id), hash_tag_id =str(hash_tag_id), status=False)

class listener(SteamListener):
    try:
        def process(self, tag, h_id):
            try:
                auth = OAuthHandler(consumer_key, consumer_secret)
                auth.set_access_token(access_token, access_secret)
                twitterStream = Steam(auth, listener())
                print "Stage-2 Process"
                twitterStream.filter(track = tag, hash_id = h_id, stall_warnings = True)
            except Exception as e:
                print ('Error in process: %s' % str(e))

        def test(self, tag, h_id, u_id, m_id):
            try:
                print "Stage-1 Test"
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
                tmp_pro_data = Tmp({
                    'movie_id':int(self.m_id),
                    'process_id':int(self.process_id),
                    'user_id':self.u_id,
                    'hash_tag_id':str(self.h_id),
                    'hash_tags':self.tag,
                    'process_status':True
                    })
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
                    tmp_data = Tmp_data({
                        'process_id':each['process_id'],
                        'user_id':each['user_id'],
                        'hash_tag_id':str(hash_id),
                        'created_at':str(a['created_at']),
                        'tweet_id':a['id'],
                        'tweet':a['text'],
                        'geo':a['geo'],
                        'coordinates':a['coordinates'],
                        'place':a['place'],
                        'language':a['lang']
                        })
                    tmp_data.save()

                    #Tweet Users
                    # user_data = Tweet_user({
                    #     'id':a['user']['id'],
                    #     'name':a['user']['name'],
                    #     'screen_name':a['user']['screen_name'],
                    #     'location':a['user']['location'],
                    #     'followers_count':a['user']['followers_count'],
                    #     'friends_count':a['user']['friends_count'],
                    #     'favourites_count':a['user']['favourites_count'],
                    #     'profile_image_url_https':a['user']['profile_image_url_https']
                    # })
                    # user_data.save()
                    
                    #Sentiment Analysis for each tweet
                    sentiment = self.sentiment(a['text'])
                    twt_sent = Tweet({
                        'user_id':each['user_id'],
                        'process_id':each['process_id'],
                        'hash_tag_id':str(hash_id),
                        'movie_id':each['movie_id'],
                        'tweet':a['text'],'sentiment':sentiment
                    })
                    twt_sent.save()   
            
            except BaseException as e:
                print('Error on_data: %s' % str(e))
            return "Sucess" 
        
        def sentiment(self, tweet):
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

if __name__ == "__main__":
    app.run(host = '0.0.0.0', port = 7000, debug = True)