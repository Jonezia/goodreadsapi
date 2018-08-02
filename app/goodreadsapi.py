import os

from flask import Flask, render_template, request, session, url_for, escape, flash, redirect
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

#export DATABASE_URL=postgres://utghlhxnukoghb:d2c56b981ec9b5e71dcb702cde71369bf5a616f4a01666331f92ac78db608690@ec2-54-217-235-166.eu-west-1.compute.amazonaws.com:5432/d6lo9nlkfrqrtr

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

app.secret_key = 'adamiscool'

#Logging in from login.html to home.html
@app.route('/', methods=['GET','POST'])
def home_template():
    if request.method == 'GET':
        homemessage = ""
        if session.get('username') is None or session['username'] == "":
            homemessage = "You are not logged in"
            loggedin = False
        else:
            homemessage = "You are logged in as %s" % escape(session['username'])
            loggedin = True
        return render_template('home.html',homemessage=homemessage, loggedin=loggedin)
    elif request.method == 'POST':
        databasepass = db.execute("SELECT password FROM users WHERE username=:username",
        {"username": request.form['username']}).fetchone()
        if request.form['password'] == databasepass.password:
            session['username']=request.form['username']
            flash('You have been successfully logged in')
            return redirect(url_for('home_template'))
        else:
            flash("login failed, please retry")
            return redirect(url_for('login_template'))

#Registering a new account from register.html to login.html
@app.route('/login', methods=['GET','POST'])
def login_template():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        if request.form['password'] == request.form['confirmpassword']:
            if db.execute("SELECT * FROM users WHERE username=:username",
            {"username": request.form['username']}).fetchone() == None:
                db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                {"username": request.form['username'], "password": request.form['password']})
                db.commit()
                flash('You have successfully registered an account')
                return redirect(url_for('login_template'))
            else:
                flash('This username is in use')
                return redirect(url_for('register_template'))
        else:
            flash("Passwords do not match, please retry")
            return redirect(url_for('register_template'))

@app.route('/register')
def register_template():
    return render_template('register.html')

@app.route('/logout')
def logout_template():
    session.pop('username', None)
    flash("You have been successfully logged out")
    return redirect(url_for('home_template'))

@app.route('/search', methods=['GET','POST'])
def search_template():
    if request.method == 'GET':
        return render_template('search.html',method="get")
    elif request.method == 'POST':
        query = '%'+request.form['query']+'%'
        results = db.execute("SELECT * FROM books WHERE isbn ILIKE :query \
        OR title ILIKE :query OR author ILIKE :query OR year ILIKE :query", {"query":query}).fetchall()
        return render_template('search.html', results=results, method="post")

#Personalised page of book with isbn as /book/"isbn"
@app.route('/book/<string:isbn>', methods=['GET','POST'])
def book_template(isbn):
    if request.method == 'GET':
        book = db.execute("SELECT isbn,title,author,year FROM books WHERE isbn=:isbn LIMIT 1",
        {"isbn":isbn}).fetchone()
        bookinfo = db.execute("SELECT username,review FROM books JOIN reviews \
        ON books.isbn = reviews.isbn WHERE books.isbn=:isbn",{"isbn":isbn}).fetchall()
        return render_template('book.html', isbn=book.isbn,title=book.title, author=book.author,
        year=book.year, bookinfo=bookinfo)
    elif request.method == 'POST':
        db.execute("INSERT INTO reviews (isbn, username, review) VALUES (:isbn, :username, :review)",
        {"isbn":isbn, "username":session['username'], "review":request.form['review']})
        db.commit()
        return redirect(url_for('book_template',isbn=isbn))

#Profile page with username as /user/"username"
@app.route('/profile/<string:username>')
def profile_template(username):
    reviews = db.execute("SELECT title,review FROM books JOIN reviews ON \
    books.isbn = reviews.isbn WHERE reviews.username=:username",{"username":username}).fetchall()
    return render_template('profile.html',username=username.capitalize(),reviews=reviews)
