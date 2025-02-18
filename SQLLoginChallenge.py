from __main__ import app
from flask import Flask
from flask import Flask, redirect, url_for, request, render_template, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from sqlalchemy import Integer, String, select
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, LoginManager, login_user, login_required, current_user, logout_user

#@app.route('/',subdomain='chall2')
#def chall2Home():

 #   return render_template('SQLLoginChallenge/index.html')