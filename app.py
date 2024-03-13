from .models import DB, DBUser, Tweet
from flask import Flask, render_template, request
from .twitter import add_or_update_user
from .predict import predict_user

def create_app():

    app = Flask(__name__)

    # database configurations
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # regiseter our database wsith the app
    DB.init_app(app)

    @app.route('/')
    def root():
        users = DBUser.query.all()
        return render_template('base.html', title='Home', users=users)
    
    @app.route('/reset')
    def reset():
        # drop all database tables
        DB.drop_all()
        # recreate alll database tables according to the indicated schema in models.py
        DB.create_all()
        return render_template('base.html', title='Reset Database')
    
    @app.route('/populate')
    def populate():
        #create two fake users
        add_or_update_user('austen')
        add_or_update_user('nasa')
        return render_template('base.html', title='Popilate')

        # save the changes just made to the database
        # 'commit' trhe database changes
    
    @app.route('/iris')
    def iris():    
        from sklearn.datasets import load_iris
        from sklearn.linear_model import LogisticRegression
        X, y = load_iris(return_X_y=True)
        clf = LogisticRegression(random_state=0,
                                 solver='lbfgs',
                                 multi_class='multinomial').fit(X, y)

        return str(clf.predict(X[:2, :]))
    
    @app.route('/update')
    def update():
        users = DBUser.query.all()
        usernames = []
        for user in users:
            usernames.append(user.username)

        for username in usernames:
            add_or_update_user(username)

    @app.route('/user', methods=['POST'])
    @app.route('/user/<username>', methods=['GET'])
    def user(username=None, message=''):

        username = username or request.values['user_name']

        try:
            if request.method == 'POST':
                add_or_update_user(username)
                message = f'User "{username}" has been successfully added!'

            tweets = DBUser.query.filter(DBUser.username==username).one().tweets

        except Exception as e:
            message = f'Error adding {username}: {e}'
            tweets = []

        return render_template('user.html',
                               title=username,
                               tweets=tweets,
                               message=message)

    @app.route('/compare', methods=['POST'])
    def compare():
        user0, user1 = sorted([request.values['user0'], request.values['user1']])
        hypo_tweet_text = request.values['tweet_text']

        if user0 == user1:
            message = 'Cannot compate a user to themselves'
        else:
            prediction = predict_user(user0, user1, hypo_tweet_text)

            if prediction:
                message = f'"{hypo_tweet_text}" is more likely to be said by {user1} than by {user0}'
            else:
                message = f'"{hypo_tweet_text}" is more likely to be said by {user0} than by {user1}'

        return render_template('prediction.html', title ='Prediction', message=message)
    
    return app
