import os

from flask import Flask, render_template, request, session, url_for, escape, flash, redirect
#from sqlalchemy import create_engine
#from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

#engine = create_engine(os.GETenv("DATABASE_URL"))
#db = scoped_session(sessionmaker(bind=engine))

app.secret_key = 'adamiscool'

@app.route('/', methods=['GET','POST'])
def home_template():
    if request.method == 'GET':
        homemessage = ""
        if session.get('username') is None or session['username'] == "":
            homemessage = "You are not logged in"
        else:
            homemessage = "You are logged in as %s" % escape(session['username'])
        return render_template('home.html',homemessage=homemessage)
    elif request.method == 'POST':
        if request.form['password'] == userdatabase[request.form['username']]:
            session['username']=request.form['username']
            flash('You have been successfully logged in')
            return redirect(url_for('home_template'))
        else:
            flash("login failed, please retry")
            return redirect(url_for('login_template'))

userdatabase = {"admin":"adminpassword","adam":"adampassword"}

@app.route('/login', methods=['GET','POST'])
def login_template():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        if request.form['password'] == request.form['confirmpassword']:
            if request.form['username'] in userdatabase:
                flash('This username is in use')
                return redirect(url_for('register_template'))
            else:
                userdatabase[request.form['username']] = request.form['password']
                flash('You have successfully registered an account')
                return redirect(url_for('login_template'))
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

@app.route('/search')
def search_template():
    if request.method == 'GET':
        return render_template('search.html')
    elif request.method == 'POST':
        results = db.execute("SELECT * FROM flights WHERE origin LIKE '%'+request.form['query']+'%'")
        return render_template('search.html', results=results)

@app.route('/book')
def book_template():
    return render_template('book.html')
