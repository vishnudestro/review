from mongothon import Schema, create_model
from datetime import datetime

logs_schema = Schema({
    "status":{"type": basestring, "required": True},
    "movie_id":{"type": int, "required": True},
    "user_id":{"type": basestring, "required": True},
    "timestamp":{"type": datetime, "required": True, 'default':datetime.now}
})

tags_schema = Schema({
    "movie_id":{"type": int, "required": True},
    "hash_tag_id":{"type": basestring, "required": True},
    "hash_tags":{"type": list, "required": True},
    "status":{"type": basestring, "required": True},
    "active":{"type": bool, "required": True, "default":False},
    "user_id":{"type": basestring, "required": True}
})

tmp_process_schema = Schema({
    "movie_id":{"type": int, "required": True},
    "process_id":{"type": int, "required": True},
    "user_id":{"type": basestring, "required": True},
    "hash_tag_id":{"type": basestring, "required": True},
    "hash_tags":{"type": list, "required": True},
    "process_status":{"type": bool, "required": True, "default":False}
})

tmp_data_schema = Schema({
    "process_id":{"type": int, "required": True},
    "user_id":{"type": basestring, "required": True},
    "hash_tag_id":{"type": basestring, "required": True},
    "created_at":{"type": basestring, "required": True},
    "tweet_id":{"type": int, "required": True},
    "tweet":{"type": basestring, "required": True},
    "geo":{"type": basestring,"default":'null'},
    "coordinates":{"type": basestring,"default":'null'},
	"place":{"type": basestring, "default":'null'},
    "language":{"type": basestring, "required": True,"default":'null'}
})

tweet_sentiment_schema = Schema({
    "user_id":{"type": basestring, "required": True},
    "process_id":{"type": int, "required": True},
    "movie_id":{"type": int, "required": True},
    "hash_tag_id":{"type": basestring, "required": True},
    "tweet":{"type": basestring, "required": True},
    "sentiment":{"type": basestring, "required": True}
})

hashtag_sentiment_schema = Schema({
    "process_id":{"type": int, "required": True},
    "user_id":{"type": basestring, "required": True},
    "movie_id":{"type": int, "required": True},
    "hash_tag_id":{"type": basestring, "required": True},
    "positive_percent":{"type": int, "required": True, "default":0},
    "negative_percent":{"type": int, "required": True, "default":0},
    "neutral_percent":{"type": int, "required": True, "default":0}
})

cluster_report_schema = Schema({
    "user_id":{"type": basestring, "required": True},
    "movie_id":{"type": int, "required": True},
    "hash_tag_id":{"type": basestring, "required": True},
    "process_id":{"type": int, "required": True},
    "tweet_id":{"type": int, "required": True},
    "tweet_type":{"type": int, "required": True}
})

tweet_user_schema = Schema({
    "id":{"type": int, "required": True},
    "name":{"type": basestring, "required": True},
    "screen_name":{"type": basestring, "required": True},
    "location":{"type": basestring, "default":'null'},
    "followers_count":{"type": int, "required": True, "default":0},
    "friends_count":{"type": int, "required": True, "default":0},
    "favourites_count":{"type": int, "required": True, "default":0},
    "profile_image_url_https":{"type": basestring, "required": True}
})