#Remember you have deprecated to Flask 2.3.3

from flask import Flask, redirect, url_for, request, render_template, jsonify, flash, send_file, Blueprint, render_template_string
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from sqlalchemy import Integer, String, select
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user
from flask_mailman import EmailMessage, Mail
import time
import boto3
from botocore.exceptions import ClientError
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

def get_secret():
   secret_name = "rds!db-1c7aa2ab-fe9c-4980-9055-06a0761afac4"
   region_name = "eu-west-2"

   # Create a Secrets Manager client
   session = boto3.session.Session()
   client = session.client(
      service_name='secretsmanager',
      region_name=region_name
   )

   try:
      get_secret_value_response = client.get_secret_value(
         SecretId=secret_name
      )
   except ClientError as e:
      # For a list of exceptions thrown, see
      # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
      raise e

   secret = get_secret_value_response['SecretString']
   return secret.split("\"")[7]

db = SQLAlchemy()

application = Flask(__name__)
application.secret_key = "super secret key" #DO NOT LEAVE THIS LIKE THIS

application.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'email-smtp.eu-west-2.amazonaws.com',
    MAIL_PORT = 465,
    MAIL_USE_TLS = False,
    MAIL_USE_SSL = True,
    MAIL_USERNAME = 'AKIAZB2ULO6MVKB56G6M',
    MAIL_PASSWORD = 'BAsM1HZc4wtr337hMZTmhnXHYe77Bev71kPlCwKQqu+I',
    MAIL_DEFAULT_SENDER = 'noreply@involuntaryctf.net',
))

application.config["RESET_PASS_TOKEN_MAX_AGE"]=600

mail = Mail()
mail.init_app(application)

db_name = 'CTF.db'

application.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://admin:{get_secret()}@ctf-database-1.cv64kuysmh9b.eu-west-2.rds.amazonaws.com:3306/CTF'

application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

# initialize the app with Flask-SQLAlchemy
db.init_app(application)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(application)

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

   def generate_reset_password_token(self):
      serializer = URLSafeTimedSerializer(application.config["SECRET_KEY"])

      return serializer.dumps(self.email, salt=self.passwords)

   @staticmethod
   def validate_reset_password_token(token: str, user_id: int):
      user = db.session.get(Users, user_id)

      if user is None:
            return None

      serializer = URLSafeTimedSerializer(application.config["SECRET_KEY"])
      try:
            token_user_email = serializer.loads(
               token,
               max_age=application.config["RESET_PASS_TOKEN_MAX_AGE"],
               salt=user.passwords,
            )
      except (BadSignature, SignatureExpired):
            return None

      if token_user_email != user.email:
            return None

      return user

class Challenges(db.Model):
   challengeID = db.Column(db.Integer, primary_key=True)
   challengeName = db.Column(db.String(40),unique=True, nullable=False)
   flagText = db.Column(db.String(40), unique=True, nullable=False)
   scoreVal = db.Column(db.Integer, unique=False, nullable=False)
   challengeType = db.Column(db.String(50),unique=False, nullable=True)

class ChallengesCompleted(db.Model):
   userID = db.Column(db.Integer, primary_key=True)
   challenge1 = db.Column(db.Boolean)
   challenge2 = db.Column(db.Boolean)
   challenge3 = db.Column(db.Boolean)
   challenge4 = db.Column(db.Boolean)
   challenge5 = db.Column(db.Boolean)
   challenge6 = db.Column(db.Boolean)
   challenge7 = db.Column(db.Boolean)
   challenge8 = db.Column(db.Boolean)
   challenge9 = db.Column(db.Boolean)


with application.app_context():
    db.create_all()


@application.route('/')
def home():
   challengesList=[]
   taskTypesList=["misc", "web exploitation", "forensics", "reversing", "cryptography"]
   
   beginCTF=(time.time()>1751047200)   #1751047200

   if not current_user.is_anonymous:
      if current_user.name=="involuntary":
         admin=True

   if beginCTF or admin:
      for i in range(5):
         challengesQueryText=text(f"SELECT challengeID, challengeName, scoreVal FROM challenges WHERE challengeType=\"{taskTypesList[i]}\"")
         challengesList.append(db.session.execute(challengesQueryText).mappings().all())

      if current_user.is_anonymous:
         userChallengesCompleted=[]
      else:      
         challengesCompletedQueryText=text(f"SELECT * FROM challenges_completed WHERE userID={current_user.id}")
         userChallengesCompleted=list(db.session.execute(challengesCompletedQueryText).mappings().all()[0].items())
      return render_template('index.html',taskTypesList=taskTypesList ,challenges=challengesList,beginCTF=beginCTF, challengesCompleted=userChallengesCompleted, admin=admin)

   else:
      return render_template('index.html', beginCTF=beginCTF, admin=admin)
   
@application.route('/',methods={"POST"})
def flagSubmit():
   flagText=request.form.get('flag')
   flag=Challenges.query.filter_by(flagText=flagText).first()

   challengesCompleted=False
   if flag:
      selectText=text(f"SELECT challenge{flag.challengeID} FROM challenges_completed WHERE userID={current_user.id}")
      challengesCompleted=list(db.session.execute(selectText).mappings().all()[0].items())[0][1]

   if not flag:
      flash("That's not a valid flag. Try again.")
      return redirect(url_for('home'))
   elif challengesCompleted:
      flash("You've submitted that flag before")
      return redirect(url_for('home'))
   else:
      updateChallengeComplete=text(f"UPDATE challenges_completed SET challenge{flag.challengeID}=1 WHERE userID={current_user.id}")
      db.session.execute(updateChallengeComplete)
      current_user.score+=flag.scoreVal
      flash("Congratulations on a correct flag")
      db.session.commit()

   return redirect(url_for('home'))

@application.route('/how-to-play')
def howToPlay():
   return render_template('how-to-play.html')

@application.route('/leaderboard')
def leaderboard():
   userQueryText=text("SELECT name,score FROM users")

   usersAndScores=db.session.execute(userQueryText).mappings().all()
   usersAndScores = sorted(usersAndScores, key=lambda d: d['score'], reverse=True)
   return render_template('leaderboard.html',users=usersAndScores, usersLength=len(usersAndScores))

@application.route('/login')
def login():
   return render_template('login.html')

@application.route('/login', methods={'POST'})
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

@application.route('/signup')
def signup():
   return render_template('signup.html')

@application.route('/signup', methods=['POST'])
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
   new_challengeCompleted = ChallengesCompleted(challenge1=0, challenge2=0,challenge3=0,challenge4=0,challenge5=0,challenge6=0,challenge7=0,challenge8=0,challenge9=0)

   db.session.add(new_user)
   db.session.add(new_challengeCompleted)
   db.session.commit()

   return redirect(url_for('login'))

@application.route('/logout')
@login_required
def logout():
   logout_user()
   return redirect('/')

if time.time()>1751047200:
   @application.route('/downloadTimeline')
   @login_required
   def downloadTimeline():
      path='challenges/Forensics/timeline challenge/files.zip'
      #path='/'
      return send_file(path, as_attachment=True)

   @application.route('/downloadFlagDoesntBite')
   @login_required
   def downloadFlagDoesntBite():
      path='challenges/Reverse engineering/basic assembly/a.out'
      #path='/'
      return send_file(path, as_attachment=True)

   @application.route('/downloadBasicPython')
   @login_required
   def downloadBasicPython():
      path='challenges/Reverse engineering/Basic python/basicPython.py'
      #path='/'
      return send_file(path, as_attachment=True)

   @application.route('/downloadInGoodForm')
   @login_required
   def downloadInGoodForm():
      path='challenges/Reverse engineering/In good form/GoodForm.c'
      return send_file(path, as_attachment=True)


@application.route('/reset-email', methods=['POST'])
@login_required
def changeEmail():
   email = request.form.get('newEmail')
   password = request.form.get('password')

   user = Users.query.filter_by(name=current_user.name).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
   if not user or not check_password_hash(user.passwords, password):
        flash('Incorrect password')
        return redirect('/') # if the user doesn't exist or password is wrong, reload the page

   if current_user.email==email:
      flash('Must be a new email')
      return redirect('/')

   query=text(f"UPDATE users SET email='{email}' WHERE id={current_user.id};")
   db.session.execute(query)
   db.session.commit()
   return redirect('/')

@application.route('/reset-password', methods=['POST'])
@login_required
def changePassword():
   currentPassword = request.form.get('currentPassword')
   newPassword= request.form.get('newPassword')
   hashedNewPassword=generate_password_hash(newPassword, method='pbkdf2:sha256')

   user = Users.query.filter_by(name=current_user.name).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
   if not user or not check_password_hash(user.passwords, currentPassword):
      flash('Incorrect password')
      return redirect('/') # if the user doesn't exist or password is wrong, reload the page
   elif current_user.passwords==hashedNewPassword:
      flash('Can\'t have the same password')
      return redirect('/')

   query=text(f"UPDATE users SET passwords='{hashedNewPassword}' WHERE id={current_user.id};")
   db.session.execute(query)
   db.session.commit()
   flash('Password changed')

   return redirect('/')



def send_reset_password_email(user):
    reset_password_url = url_for(
        "forgotPasswordReset",
        token=user.generate_reset_password_token(),
        user_id=user.id,
        _external=True,
    )

    email_body = render_template(
        'reset_password_email_content.html', reset_password_url=reset_password_url
    )

    message = EmailMessage(
        subject="Reset your password",
        body=email_body,
        to=[user.email],
    )
    message.content_subtype = "html"

    message.send()


@application.route('/forgot-password')
def forgotPassword():
   return render_template('forgot-password.html')

@application.route('/forgot-password', methods=['POST'])
def forgotPasswordPost():
   if current_user.is_authenticated:
     return redirect('/')
   
   formEmail=request.form.get('email')

   user = Users.query.filter_by(email=formEmail).first()

   if user:
      send_reset_password_email(user)

   flash(
      "Instructions to reset your password were sent to your email address,"
      " if it exists in our system."
   )

   return redirect('/forgot-password')

@application.route("/reset_password/<token>/<int:user_id>")
def forgotPasswordReset(token, user_id):
   if current_user.is_authenticated:
         return redirect('/')

   user = Users.validate_reset_password_token(token, user_id)
   if not user:
      return render_template("reset-password.html", error=True)   

   return render_template('reset-password.html', error=False)

@application.route("/reset_password/<token>/<int:user_id>",methods=['POST'])
def forgotPasswordResetPost(token, user_id):
   if current_user.is_authenticated:
         return redirect('/')

   user = Users.validate_reset_password_token(token, user_id)
   if not user:
      return render_template("reset-password.html", error=True)   

   currentPassword = request.form.get('currentPassword')
   newPassword= request.form.get('newPassword')

   hashedNewPassword=generate_password_hash(newPassword, method='pbkdf2:sha256')

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
   if user.passwords==hashedNewPassword:
      flash('Can\'t have the same password')
      return redirect(f'/reset_password/{token}/{user_id}')

   query=text(f"UPDATE users SET passwords='{hashedNewPassword}' WHERE id={user.id};")
   db.session.execute(query)
   db.session.commit()
   
   return redirect('/login')


if time.time()>1751047200:
   @application.route('/rollthedice')
   def rollTheDice():
      return render_template('rollTheDice.html')

   @application.route('/rollthedice/flag',methods=['POST'])
   def rollTheDiceFlag():
      request_data = request.get_json()
      randomNum=request_data['number']
      guess=request_data['guess']

      flag="!FLAG!{N0t_so_r4nd0m!!}!FLAG! "

      if randomNum==guess:
         return {"flag":flag}
      else:
         return {"flag":f"incorrect guess again. The number was {randomNum}"}

if __name__ == '__main__':
   website_url='involuntaryCTF:5000'
   application.config['SERVER_NAME']=website_url
   application.run(debug=False)