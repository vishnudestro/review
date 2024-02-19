import multiprocessing
from tweepy import Stream
from tweepy import OAuthHandler
from steaming import SteamListener, Steam
import time
import json
import os
import pymongo
from pymongo import MongoClient

client = MongoClient('localhost', 19823)
db = client.demo

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

class listener(SteamListener, Steam):
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
                # db.tmp.insert({'movie_id':self.m_id,'process_id':self.process_id,'user_id':self.u_id,'hash_tag_id':self.h_id,'hash_tags':self.tag,'process_status':True})
                return self.process_id
            except Exception as e:
                print ('Error in test: %s' % str(e))   
        
        def on_data(self,data, hash_id):
            try:
                a = json.loads(data)
                print a['user']['id']
                print a['user']['name']
                print a['user']['screen_name']
                print a['user']['location']
                print a['user']['followers_count']
                print a['user']['friends_count']
                print a['user']['favourites_count']
                print a['user']['profile_image_url_https']
                # for each in a['user']:
                #     print each['screen_name']
                print '===================================='    
            except BaseException as e:
                print('Error on_data: %s' % str(e))
            return "Sucess" 
    
    except Exception as e:
        print ('error in class: %s' % str(e))

def main():
    i = ['vijay']
    t = Myclass(i, 2, 3, 4)
    t.myfunc1()

if __name__ == '__main__':
    main()