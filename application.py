import os
import requests
import json
from functools import wraps
from datetime import date
from flask import Flask, session,render_template,request,flash,redirect,url_for,g,abort,jsonify
from flask_session import Session
from sqlalchemy import create_engine,or_,and_,func 
from sqlalchemy.orm import scoped_session, sessionmaker

#Import table definitions
from models import *


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
## this enable secret (note to self)
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
Session(app)


# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))

db = scoped_session(sessionmaker(bind=engine))

class User:
    def __init__(self,id,username,password):
        self.id = id
        self.username = username
        self.password = password

    def __repr__(self):
        return f'<User: {self.username}>'

def login_reguired(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash("Login Required")
            return redirect(url_for('login'))
    return wrap

@app.before_request
def before_request():
    if 'logged_in' in session:
        user = session['user_name']
        g.user = user
    
        
@app.route("/")
def index():
    session.clear()
    return render_template("login.html")



@app.route("/login", methods=['GET','POST'])
def login():
    if 'logged_in' in session:
        redirect(url_for('search'))
    session.clear()
   
    if request.method == 'POST':
   
        user = request.form.get("username")
        password = request.form.get('password')
        try:
            x = LOGINID.query.filter_by(username = user).first()
            if  x and x.password == password:
                session['user_name'] = x.username
                session['logged_in'] = True
                return redirect(url_for('search'))
            else:
                return render_template('login.html',error="Invalid Username or Password")
   
        except:
            flash("Invalid User or Password")
            return render_template('login.html',error="Invalid Username or Password")
   
    return render_template('login.html')


@app.route('/signup', methods = ['GET','POST']) #, methods = ['Post']
def signup():
    
    session.clear()
    if request.method == "POST" and 'logged_in' not in session:
        user = request.form.get('username')
        password = request.form.get('password')
        passwords = request.form.get('passwords') 
        email = request.form.get('email')
        x = LOGINID.query.filter_by(username = user).first()
        emailcheck = LOGINID.query.filter_by(email = email).first()
  
        if password != passwords:
             return render_template('signup.html',error="Password does not match.")    
        elif x:
          return render_template('signup.html',error="Username exit. Please enter a unique username.")
        elif emailcheck:
            return render_template('signup.html',error="Email already exist. Please enter a unqiue email.")
        else:
            db.add(LOGINID(email= email,username = user, password = password))
            db.commit()
            session['logged_in'] = True
            session['user_name'] = user
            return redirect(url_for('search'))    
            
    return render_template('signup.html')
                

@app.route('/search',methods = ['GET','POST'])
@login_reguired
def search():
    if request.method == 'GET':

        query  =  request.args.get('q')
        if not query:
            return render_template("index.html")
        
        if len(query) > 4 or not query.isnumeric():
            year = 0
        else:
            year = query

        query = '%' + query + '%'   

        results = BOOK.query.filter(or_(BOOK.isbn.ilike(query),
                                        BOOK.title.ilike(query),
                                        BOOK.author.ilike(query),BOOK.year == year)).all()
        
        if not results:
            return render_template("index.html",error= "Item not found")

        return render_template("index.html",results=results)
    return render_template('index.html')


@app.route('/book/<string:isbn>', methods=['GET','POST'])
@login_reguired
def book(isbn):
    username = session['user_name']
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "E5mjnIIOojFeFByFtx6RAQ", "isbns": isbn})
    result = BOOK.query.filter_by(isbn = isbn).first()

    if not res:
        abort(404)
    x = json.loads(res.text)
       
    goodreadAverage = (x['books'][0]['average_rating'])
    writingCount = x['books'][0]['work_ratings_count']
    if not goodreadAverage:
        goodreadAverage = 0
    if not writingCount:
        writingCount = 0
        
    check = RATING.query.filter(and_(RATING.book_id == isbn,RATING.username == username)).first()
    if check:
        postExist = True
    else:
        postExist = False

    if  postExist is False and request.method == 'POST':
        review = (request.form.get('comment'))
        rating = (request.form.get('option'))
        query = RATING(review = review, rating = rating, review_date = date.today(),book_id = isbn ,username = username)
        db.add(query)
        db.commit()
        redirect('/book/'+isbn)
    
    
    
    return render_template('bookpage.html',result=result,postExist=postExist,goodreadAverage=goodreadAverage,writingCount=writingCount)

@app.route('/api/<string:isbn>', methods = ['GET'])
def api(isbn):
    
    if request.method == 'GET':
        result = BOOK.query.filter_by(isbn = isbn).first()
        if not result:
            abort(404)
        rating = RATING.query.filter_by(book_id = isbn).count()
        average = db.execute("Select ROUND(AVG(RATING),2) from RATING").fetchone()  
        if average is None:
            average = 0
        else:
            average = float(average[0])

        x = {
            "title": result.title,
            "author": result.author,
            "year": result.year,
            "isbn": result.isbn,
            "review_count": rating,
            "average_score": average
        }
        try:
            y = jsonify.dumps(x)
            return y 
        except:
            return abort('404')

    return render_template('404.html')


@app.errorhandler(404)
def page_note_found(e):
    return render_template('404.html')


@app.route('/signout')
@login_reguired
def signout():
    session.clear()
    flash("You were logged out")
    return redirect(url_for('login'))



# @app.route("/hello", methods=["POST"])
# def hello():
#     userName = request.form.get("userName")
#     pWord = request.form.get("pWord")
   
#     return "yes"
# @app.route("/logout")
# def logout():
#     session.clear()
#     return login()
# res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "E5mjnIIOojFeFByFtx6RAQ", "isbns": "9781632168146"})
# print(res.json())
    # db.execute("Create Table loginId( id Serial PRIMARY KEY, userName VARCHAR (50) UNIQUE, password VARCHAR(50))")
    # db.execute("Insert INTO loginId(id,userName,password) VALUES('vinson','123456')")
    # check = db.execute("Select * from loginId").fetchall()
     #  login = LOGINID(email = "vinson@gmail.com",username="vinson",password="pp")
    # db.add(login)
    # db.commit()