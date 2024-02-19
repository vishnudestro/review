import urllib, json, requests
import datetime
import pymongo
import multiprocessing
from pymongo import MongoClient
import uuid
import os
import tweet as tt
import review as r
import tweet_analysis as ta
from mongothon import Schema, create_model
from db_schema import tags_schema, logs_schema, tmp_process_schema, hashtag_sentiment_schema, cluster_report_schema


client = MongoClient('localhost', 19823)
db = client.review

Tag = create_model(tags_schema, db['tags'])
Log = create_model(logs_schema, db['logs'])
Tmp = create_model(tmp_process_schema, db['tmp_process'])
Hash = create_model(hashtag_sentiment_schema, db['hash_sentiment'])
Cluster = create_model(cluster_report_schema, db['cluster_report'])

def json_load(link):
    data = requests.get(link)
    json_data = data.json()
    data.close()
    return json_data

def movie_data(page):
    try:
        upmovies = {}
        url = 'https://api.themoviedb.org/3/movie/upcoming?api_key=f0e0a9bdeb570b77abd960172e5e7abb&page='+str(page)
        movie_list = json_load(url)
        t_pages = movie_list['total_pages']
        
        for movie in movie_list['results']:
            if movie['original_language'] in upmovies: 
                upmovies[movie['original_language']].append({'movie_id' : movie['id'],
                'genre_ids': [genre(eachg) for eachg in movie['genre_ids']],
                'backdrop_path': movie['backdrop_path'],
                'original_title':movie['original_title'],
                'popularity': movie['popularity'],
                'poster_path':movie['poster_path'],
                'release_date':movie['release_date'],
                'vote_average':movie['vote_average'],
                'vote_count':movie['vote_count'],
                'overview' :movie['overview']
                })
            else: 
                upmovies[movie['original_language']] = []
                upmovies[movie['original_language']].append({'movie_id' : movie['id'],
                'genre_ids': [genre(eachg) for eachg in movie['genre_ids']],
                'backdrop_path': movie['backdrop_path'],
                'original_title':movie['original_title'],
                'popularity': movie['popularity'],
                'poster_path':movie['poster_path'],
                'release_date':movie['release_date'],
                'vote_average':movie['vote_average'],
                'vote_count':movie['vote_count'],
                'overview' :movie['overview'],
                'poster_path':movie['poster_path']
                })
        return upmovies,t_pages
    except Exception as e:
       print ('Error in movie data', e)
   
#Finding Movie genre
def genre(genre_id):
    try:
        for each in json_genre['genres']:
            if each['id'] == genre_id:
                return each['name']
    except Exception as e:
        print ('Error in genre', e)

#view movie by id:
def view_movie(movie_id):
    try:
        url = 'http://api.themoviedb.org/3/movie/'+str(movie_id)+'?api_key=f0e0a9bdeb570b77abd960172e5e7abb'
        json_data = json_load(url)
        return json_data  
    except Exception as e:
        print ('Error in view movie', e)

#Insert tags
def movie_tags_insert(m_id, req_data, user_id):
    try:   
        if req_data['status'] != 'stop':
            #Starts Hashtag Collection
            h_id = uuid.uuid4()
            tag_data = Tag({'movie_id':m_id,'hash_tag_id':str(h_id),'hash_tags':req_data['tags'],'status':'started','active':True, 'user_id':user_id})
            tag_data.save()
            log_data = Log({'user_id':user_id,'movie_id':m_id,'status':'started','timestamp':datetime.datetime.now()}) 
            log_data.save()
            
            #Listener Class Calling
            t = tt.Myclass(req_data['tags'], h_id, user_id, m_id)
            t.myfunc1()
            return movie_log(m_id,user_id)
        else:
            return None
    except Exception as e:
        print ('Error in insert', e)

#Update tags and Logs
def movie_tags_update(m_id, user_id, m_status):
    try:
        m_details = []
        data = db.tmp_process.find({'movie_id':m_id,'process_status':True})
        if data.count() > 0:
            #Status = Stop  
            for each in data:          
                if m_status == 'stop':
                    #Kill Process
                    print each['process_id']
                    kill_value = os.system("kill -9 "+str(each['process_id']))
                    print 'kill_value:',kill_value
                    Tag.update({'movie_id':m_id,'hash_tag_id':str(each['hash_tag_id'])},{'$set':{'status':'stopped','active':False}})
                    log_data = Log({'user_id':user_id,'movie_id':m_id,'status':'stopped','timestamp':datetime.datetime.now()}) 
                    log_data.save()
                    Tmp.update({'movie_id':m_id,'process_id':each['process_id'],'hash_tag_id':str(each['hash_tag_id'])},{'$set':{'process_status':False}})
                    
                    print 'Started Sentiment Analysis'
                    #Over all Sentiment Analysis for particular Hash tag 
                    positive, negative, neutral = ta.sentiment_report(hash_id = each['hash_tag_id'])
                    hash_data = Hash({'process_id':each['process_id'],'user_id':user_id,'movie_id':m_id,'hash_tag_id':str(each['hash_tag_id']),
                    'positive_percent':positive,'negative_percent':negative,'neutral_percent':neutral})
                    hash_data.save()

                    print 'Started Clustering'
                    #Cluster Analysis
                    tweet_id, tweet_type = ta.cluster(each['process_id'])
                    for i in range(len(tweet_id)):
                        c_data = Cluster({'process_id':each['process_id'],'user_id':user_id,'movie_id':m_id,
                        'hash_tag_id':str(each['hash_tag_id']),'tweet_id':int(tweet_id[i]),'tweet_type':int(tweet_type[i])})
                        c_data.save()
                    
                    return movie_log(m_id, user_id)
                
                #Status = Relaunch
                elif m_status == 'relaunch':
                    Tag.update({'movie_id':m_id,'hash_tag_id':each['hash_tag_id']},{'$set':{'status':'relaunched','active':True}})
                    log_data = Log({'movie_id':m_id,'status':'relaunched','timestamp':datetime.datetime.now()})              
                    log_data.save()
                    return movie_log(m_id, user_id)
        else:
            return None    
    except Exception as e:
        print ('Error in update', e)

def movie_log(movie_id, current_user_id):
    try:
        #View specific movie data  
        hash_tags =[]
        movie_view = {}
        movie_view['logs'] = []
        movie_details = db.tags.find({'movie_id':int(movie_id),'user_id':current_user_id})
        log_movie = db.logs.find({'movie_id':int(movie_id),'user_id':current_user_id})
        movie_json = view_movie(movie_id)
        
        if movie_details.count() > 0:
            for each in movie_details:
                hash_tags.append([eachh for eachh in each['hash_tags']])
                movie_view.update({'movie_id':movie_id,
                'hash_tags':[i for i in hash_tags],
                'language':movie_json['original_language'], 
                'title':movie_json['title'],
                'genres':[eachg['name'] for eachg in movie_json['genres']],
                'runtime':movie_json['runtime'], 
                'overview':movie_json['overview'], 
                'poster_path':movie_json['poster_path'], 
                'homepage':movie_json['homepage'],
                'status': each['status'],
                'active':each['active']})
            for eachl in log_movie:
                log = ('movie id'+' '+str(eachl['movie_id'])+' '+'hash tag collection'+' '+eachl['status']+' '+'at'+' '+str(eachl['timestamp']))
                movie_view['logs'].append(log)
            return movie_view
        
        else:
            movie_view.update({'movie_id':movie_id,'language':movie_json['original_language'],'active':False,
            'title':movie_json['title'],
            'runtime':movie_json['runtime'], 
            'overview':movie_json['overview'],
            'poster_path':movie_json['poster_path'],
            'genres':[eachg['name'] for eachg in movie_json['genres']],
            'homepage':movie_json['homepage']})
            return movie_view
    
    except Exception as e:
        print ('Error in movie log', e)

#genre
genre_url = 'https://api.themoviedb.org/3/genre/movie/list?api_key=f0e0a9bdeb570b77abd960172e5e7abb&language=en-US'
json_genre = json_load(genre_url)


