#!/usr/bin/env python
# encoding: utf-8

import os
import tweepy # https://github.com/tweepy/tweepy
import csv
import time

# Twitter API credentials
consumer_key = os.environ["TWITTER_KEY"]
consumer_secret = os.environ["TWITTER_SECRET"]
access_key = os.environ["TWITTER_ACCESS_KEY"]
access_secret = os.environ["TWITTER_ACCESS_SECRET"]

# https://gist.github.com/yanofsky/5436496
requests = 0
def get_all_tweets(tweepy_api, screen_name):
    global requests
    # Twitter only allows access to a users most 
    # recent 3240 tweets with this method
        
    # initialize a list to hold all the tweepy Tweets
    alltweets = []	
        
    # make initial request for most recent tweets 
    # (200 is the maximum allowed count)
    new_tweets = tweepy_api.user_timeline(screen_name=screen_name, count=200)
    requests += 1
    # save most recent tweets
    alltweets.extend(new_tweets)
        
    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1
        
    # keep grabbing tweets until there are no tweets left to grab
    while len(new_tweets) > 0:            
        # all subsiquent requests use the max_id 
        # param to prevent duplicates
        # rate limit 180 every 15 min
        new_tweets = tweepy_api.user_timeline(screen_name=screen_name,
                                              count=200,
                                              max_id=oldest)
        
        requests +=1
        print "requests: ", requests
        # save most recent tweets
        alltweets.extend(new_tweets)
                
        # update the id of the oldest tweet less one
        oldest = alltweets[-1].id - 1
        print "...%s tweets downloaded" % (len(alltweets))
        time.sleep(60)

    # create list to be serialized
    outtweets = [{"author_id": tweet.author.id,
                  "author_name": tweet.author.screen_name,
                  "tweet_id": tweet.id_str, 
                  "created_at": tweet.created_at.isoformat(), 
                  "lang": tweet.lang,
                  "text": tweet.text.encode("utf-8"),
                  "favorite_count": tweet.favorite_count,
                  "retweet_count": tweet.retweet_count,
                  "replay_status_id": tweet.in_reply_to_status_id,
                  "reply_user_id": tweet.in_reply_to_user_id,
                  "reply_user_name": tweet.in_reply_to_screen_name,
                  "coordinates": tweet.coordinates,
                  "place_country_code": tweet.place.country_code if tweet.place else None,
                  "place_full_name": tweet.place.full_name if tweet.place else None,
                  "place_bounding_box": tweet.place.bounding_box.coordinates if tweet.place else None,
                  "place_id": tweet.place.id if tweet.place else None,
                  "place_type": tweet.place.place_type if tweet.place else None,
                  "place_attributes": tweet.place.attributes if tweet.place else None,
                  "entities": tweet.entities,
                  "source": tweet.source} for tweet in alltweets]
    
    # dump it to json file
    out = "dumps/%s_tweet_dump.json"
    with open(out % screen_name, 'wb') as f:
        import json
        f.write(json.dumps(outtweets))
    print "Wrote JSON dump to", out % screen_name

def get_network_tweets(api, screen_name):
    # get 3200 most recent tweets from the 200 most recent friends of the user
    user = api.get_user(screen_name)
    friends = user.friends(count=200)

    if len(friends) != user.friends_count:
        print "Didn't get all friends: ", len(friends), "/", user.friends_count

    # do this instead once rate limit figured out
    # appears to be either 30 requests every 15 mintutes
    # for friend in tweepy.Cursor(api.friends, screen_name, count=200): 
    for friend in friends:
        print "Getting tweets for: ", friend.screen_name
        get_all_tweets(api, friend.screen_name)

def authenticate(user_access=False):
    # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    if user_access:
        auth.set_access_token(access_key, access_secret)
    return tweepy.API(auth)

if __name__ == '__main__':
    api = authenticate()
    get_network_tweets(api, "_raymondzeng")
