from database import db
from flask_login import UserMixin
from datetime import datetime


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password_hash = db.Column(db.String(320), nullable=False)

class Blogpost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(60), nullable=False)
    author = db.Column(db.String(20), nullable=False) ##username
    publish_date = db.Column(db.DateTime, default=datetime.now())
    category = db.Column(db.String(60), nullable=False)
    body = db.Column(db.Text)
    score = db.Column(db.Float, default=0.0)
    
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String(20), nullable=False)
    publish_date = db.Column(db.DateTime, default=datetime.now())
    parent_id = db.Column(db.Integer, nullable=False)
    body = db.Column(db.Text)