from crypt import methods
import email
from multiprocessing import Condition
from .database import db
from flask import Flask, redirect, request
from flask import render_template
from flask import current_app as app

from application.models import *
alert_error, alert_color, alert_condition, alert_message = False,'','',''
signedin = True
@app.route("/home", methods=['GET'])
def home():
    global alert_error, alert_color, alert_condition, alert_message
    if alert_error:
        alert_error = False
        template = render_template('index.html',show=True, alert_color=alert_color, alert_condition=alert_condition, alert_message=alert_message, signedin=signedin)
        alert_color, alert_condition, alert_message = '','',''
        return template
    
    return render_template('index.html', signedin=signedin)

@app.route("/", methods=['GET'])
def main():
    return render_template('index.html')

@app.route("/todo", methods=['GET'])
def todo():
    email = 'ommprakash.sahoo.eee20@iitbhu.ac.in'
    account = Account.query.filter_by(email=email).first()

    return render_template('todo.html', lists=account.lists)

@app.route("/summary", methods=['GET'])
def summary():
    return render_template('summary.html')

import re
@app.route("/signup", methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name=request.form['name']
        email=request.form['email'].strip()
        password=request.form['password']
        confirm_password=request.form['confirm_password']
        condition, error_message, error = 'Congrats','Your account is made successfully.',False
        special_char_name=re.compile('[@!$%^&*().<>?/\|}{~:]#0123456789')
        
        res = len([ele for ele in name if ele.isalpha()])
        if special_char_name.search(name) != None or res<1:
            error = True
            condition = 'Invalid Name'
            error_message = 'Only alphabates and space allowed.'
        elif '@' not in email or len(email)<3:
            error = True
            condition = 'Invalid Email'
            error_message = 'Please enter a valid Email.(Only [A-Z],[a-z],<space>,<_>,[0-9],@ allowed)'
        elif password != confirm_password:
            error = True
            condition = 'Invalid Password'
            error_message = 'Please enter both of your passwords again.'
        else:
            account = Account.query.filter_by(email=email).first()
            # peter = User.query.filter_by(username='peter').first()
            if account != None:
                error = True
                condition = 'Email Already Exists'
                error_message = 'Please provide another email.'
        if error:
            return render_template('signUp.html', show=True, color='alert-danger', condition=condition, error_message=error_message, name=name,  email=email)
        try:
            account = Account(password=password, name=name, email=email)
            db.session.add(account)
            db.session.commit()
        except:
            error = True
            condition = 'Error'
            error_message = 'Server error.'                        
            
        return render_template('signUp.html', show=True, color='alert-success', condition=condition,error_message=error_message)
        
    if request.method == 'GET':
        return render_template('signUp.html')

@app.route("/signin", methods=['POST'])
def signin():
    email=request.form['email']
    password = request.form['password']
    account = Account.query.filter_by(email=email).first()
    global alert_error, alert_color, alert_condition, alert_message, signedin

    if request.method == 'POST':
        if account is None:
            alert_error = True
            alert_condition = 'Email Not Exists'
            alert_message = 'Please provide another email.'
        elif '@' not in email or len(email)<3:
            alert_error = True
            alert_condition = 'Invalid Email'
            alert_message = 'Please enter a valid Email.(Only [A-Z],[a-z],<space>,<_>,[0-9],@ allowed)'
        elif account.password != password:
            alert_error = True
            alert_condition = 'Wrong Password'
            alert_message = 'Please provide correct password.'
        if alert_error:
            alert_color = 'alert-danger'
            return redirect('/home')

        signedin = True
        return redirect('/home')


# from application.models import Article

# @app.route("/", methods=["GET", "POST"])
# def articles():
#     app.logger.info("Inside get all articles using info")
#     articles = Article.query.all()    
#     app.logger.debug("Inside get all articles using debug")
#     return render_template("articles.html", articles=articles)

# @app.route("/articles_by/<user_name>", methods=["GET", "POST"])
# def articles_by_author(user_name):
#     articles = Article.query.filter(Article.authors.any(username=user_name))
#     return render_template("articles_by_author.html", articles=articles, username=user_name)
