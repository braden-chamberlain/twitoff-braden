from os import getenv
from twitoff import not_tweepy as tweepy
from .models import Tweet, DB
from .models import DBUser
import spacy
from twitoff.not_tweepy import API

# get our api keys from our .env file
key = getenv('TWITTER_API_KEY')
secret = getenv('TWITTER_API_KEY_SECRET')

# TWITTER_AUTH = tweepy.OAuthHandler(key, secret)
# TWITTER = tweepy.API(TWITTER_AUTH)

URL = getenv("NOT_TWITTER_URL")
TWITTER = API(URL)

def add_or_update_user(username):
    '''take a username and pull that user's data and tyweets from the API
    If this user already exists in our database then we will just check to see if
    there are any new tweets form that user taht we don't already have
    and we will add any new tweets to the DB.'''

    try:
        #get the user iformation from twitter
        twitter_user = TWITTER.get_user(screen_name=username)
        # check to see if this user is already in the database
        # is there a user with the same ID already in the database
        # if we don't already have a user we will create a new one
        db_user = (DBUser.query.get(twitter_user.id)) or DBUser(id=twitter_user.id, username=username)

        # add the user to the databse
        # this won't re-add a user if they've already been added
        DB.session.add(db_user)

        tweets = twitter_user.timeline(count=200,
                                    exclude_replies=True,
                                    include_rts=False,
                                    tweet_mode='extended',
                                    since_id=db_user.newest_tweet_id)
        # update the newest tweet id if there have been new tweets
        # since the last time this user tweeted
        if tweets:
            db_user.newest_tweet_id = tweets[0].id
        
        # add all of the individual tweets to the database

        for tweet in tweets:
            tweet_vector = vectorize_tweet(tweet.full_text)
            db_tweet = Tweet(id=tweet.id,
                            text=tweet.full_text[:300],
                            vect=tweet_vector,
                            user_id=db_user.id)
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
        
    except Exception as e:
        print(f'error processing {username}: {e}')
        raise e
    
    else:
        # save the changes ato the DB
        DB.session.commit()

    nlp = spacy.load('my_model/')
    # we have the same tool we used in the flaask shell
    # takes a tweet and vector encodes them

def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector
