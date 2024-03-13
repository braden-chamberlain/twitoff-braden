from sklearn.linear_model import LogisticRegression
import numpy as np
from .models import DBUser
from .twitter import vectorize_tweet


def predict_user(user0_username, user1_username, hypo_tweet_text):

    # grab users from the DB
    user0 = DBUser.query.filter(DBUser.username==user0_username).one()
    user1 = DBUser.query.filter(DBUser.username==user1_username).one()

    # get the word embeddings from each user
    user0_vects = np.array([tweet.vect for tweet in user0.tweets])
    user1_vects = np.array([tweet.vect for tweet in user1.tweets])

    # verticaly stack the two 2d numpy arrays to make our X matrix
    X_train = np.vstack([user0_vects, user1_vects])

    # concatenate our labels of 0 or 1 for each tweet
    zeros = np.zeros(user0_vects.shape[0])
    ones = np.ones(user1_vects.shape[0])

    y_train = np.concatenate([zeros, ones])

    # instantaite and fit a logistic regression model
    log_reg = LogisticRegression().fit(X_train, y_train)

    # vectorize the hypothetical tweet text
    # make sure it's held in a 2d numpy array rather than 1d
    hypo_tweet_vect = vectorize_tweet(hypo_tweet_text).reshape(1, -1)
    
    return log_reg.predict(hypo_tweet_vect)[0]


