#Remember you have deprecated to Flask 2.3.3

from flask import Flask, redirect, url_for, request, render_template, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from sqlalchemy import Integer, String, select
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user

db = SQLAlchemy()

app = Flask(__name__)
app.secret_key = "super secret key" #DO NOT LEAVE THIS LIKE THIS

db_name = 'flask.db'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost:3306/flask'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# initialize the app with Flask-SQLAlchemy
db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'app.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
   # since the user_id is just the primary key of our user table, use it in the query for the user
   return Users.query.get(int(user_id))

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), unique=True,nullable=False)
    score = db.Column(db.Integer, unique=False, nullable=False)
    email = db.Column(db.String(40), unique=True, nullable=False)
    passwords = db.Column(db.String(60), unique=False, nullable=False)

class Challenges(db.Model):
   challengeID = db.Column(db.Integer, primary_key=True)
   challengeName = db.Column(db.String(40),unique=True, nullable=False)
   flagText = db.Column(db.String(40), unique=True, nullable=False)
   scoreVal = db.Column(db.Integer, unique=False, nullable=False)

class ChallengesCompleted(db.Model):
   userID = db.Column(db.Integer, primary_key=True)
   challenge1 = db.Column(db.Boolean)
   challenge2 = db.Column(db.Boolean)

with app.app_context():
    db.create_all()

@app.route('/')
def home():
   print(current_user.is_anonymous)
   return render_template('index.html')

@app.route('/',methods={"POST"})
def flagSubmit():
   flagText=request.form.get('flag')
   flag=Challenges.query.filter_by(flagText=flagText).first()

   challengesCompleted=False
   if flag:
      selectText=text(f"SELECT challenge{flag.challengeID} FROM challenges_completed WHERE userID={current_user.id}")
      challengesCompleted=list(db.session.execute(selectText).mappings().all()[0].items())[0][1]

   if not flag:
      flash("That's not a valid flag. Try again.")
      return render_template('index.html') 
   elif challengesCompleted:
      flash("You've submitted that flag before")
      return render_template('index.html')
   else:
      updateChallengeComplete=text(f"UPDATE challenges_completed SET challenge{flag.challengeID}=1 WHERE userID={current_user.id}")
      db.session.execute(updateChallengeComplete)
      current_user.score+=flag.scoreVal
      db.session.commit()

   return render_template('index.html')

@app.route('/how-to-play')
def howToPlay():
   return render_template('how-to-play.html')

@app.route('/leaderboard')
def leaderboard():
   userQueryText=text("SELECT name,score FROM users")

   usersAndScores=db.session.execute(userQueryText).mappings().all()
   usersAndScores = sorted(usersAndScores, key=lambda d: d['score'], reverse=True)
   return render_template('leaderboard.html',users=usersAndScores, usersLength=len(usersAndScores))

@app.route('/login')
def login():
   return render_template('login.html')

@app.route('/login', methods={'POST'})
def login_post():
   name = request.form.get('inputUsername')
   password = request.form.get('inputPassword')
   remember = request.form.get('remember-me')

   user = Users.query.filter_by(name=name).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
   if not user or not check_password_hash(user.passwords, password):
        flash('Please check your login details and try again.')
        return redirect(url_for('login')) # if the user doesn't exist or password is wrong, reload the page

   login_user(user, remember=remember)
   return redirect('/')

@app.route('/signup')
def signup():
   return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_post():
   # code to validate and add user to database goes here
   email = request.form.get('inputEmail')
   name = request.form.get('inputUsername')
   password = request.form.get('inputPassword')

   user = Users.query.filter_by(email=email).first() or Users.query.filter_by(name=name).first() # if this returns a user, then the email already exists in database

   if user: # if a user is found, we want to redirect back to signup page so user can try again
      flash("User already exists. Pick a new username/email.")
      return redirect(url_for('signup'))

   # create a new user with the form data. Hash the password so the plaintext version isn't saved.
   new_user = Users(score=0,email=email, name=name, passwords=generate_password_hash(password, method='pbkdf2:sha256'))
   new_challengeCompleted = ChallengesCompleted(userID=2,challenge1=1, challenge2=1)

   db.session.add(new_user)
   db.session.add(new_challengeCompleted)
   db.session.commit()

   return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect('/')

if __name__ == '__main__':
   app.run(debug=True)

