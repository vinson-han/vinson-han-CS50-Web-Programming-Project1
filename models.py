from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

db = SQLAlchemy()


class LOGINID(db.Model):
    __tablename__ = "loginid"
    id = db.Column(db.Integer, primary_key =True)
    email = db.Column(db.String,nullable=False)
    username= db.Column(db.String,nullable=False)
    password= db.Column(db.String,nullable=False)
    
class BOOK(db.Model):
    __tablename__ = "book"
    isbn = db.Column(db.String,primary_key= True)
    title = db.Column(db.String,nullable=False)
    author = db.Column(db.String,nullable=False)
    year = db.Column(db.Integer,nullable=False)
    children = relationship("RATING")

class RATING(db.Model):
    __tablename__ = "rating"
    review_id = db.Column(db.Integer, primary_key=True)
    review = db.Column(db.Text,nullable=False)
    rating = db.Column(db.Integer,nullable=False)
    review_date = db.Column(db.DateTime,nullable=False)
    book_id = db.Column(db.Integer,db.ForeignKey('book.isbn'),nullable=False)
    username = db.Column(db.String,nullable=False)