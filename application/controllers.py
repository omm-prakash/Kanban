from .database import db
from flask import Flask, redirect, request
from flask import render_template
from flask import current_app as app
from datetime import datetime

from application.models import *

alert_error, alert_color, alert_condition, alert_message = False,'','',''
signedin,name,email = False,'',''
@app.route("/home", methods=['GET'])
def home():
    global alert_error, alert_color, alert_condition, alert_message
    if alert_error:
        alert_error = False
        template = render_template('index.html',show=True, alert_color=alert_color, alert_condition=alert_condition, alert_message=alert_message, signedin=signedin)
        alert_color, alert_condition, alert_message = '','',''
        return template
    
    return render_template('index.html', signedin=signedin,name=name,email=email)

@app.route("/", methods=['GET'])
def main():
    return render_template('index.html')

@app.route("/todo", methods=['GET'])
def todo():
    global signedin, email, name
    global alert_error, alert_color, alert_condition, alert_message
    lists = []
    if signedin:
        account = Account.query.filter_by(email=email).first()
        if account.lists is not None:
            lists = account.lists
    if alert_error:
        alert_error = False
        template = render_template('todo.html',show=True, alert_color=alert_color, alert_condition=alert_condition, alert_message=alert_message, lists=lists, signedin=signedin, email=email, name=name)
        alert_color, alert_condition, alert_message = '','',''
        return template
    # print(lists,'--------------------------------------')    
    return render_template('todo.html', lists=lists, signedin=signedin, email=email, name=name)

@app.route('/create_list', methods=['POST'])
def create_list():
    global alert_error, alert_color, alert_condition, alert_message, email
    if not signedin:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Not SignedIn'
        alert_message = 'Please signin to add a list'
        return redirect('/todo')
    name_exist = List.query.filter_by(list_name=request.form['list_name'].strip()).first() is not None
    if name_exist:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'List Exists'
        alert_message = 'List name already exists, try another.'
        return redirect('/todo')
    try:
        account = Account.query.filter_by(email=email).first()
        list = List(list_name=request.form['list_name'].strip(), list_desc=request.form['list_desc'].strip())
        db.session.add(list)
        account.lists.append(list)
        db.session.commit()
        return redirect('/todo')
    except:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Server Error'
        alert_message = 'Got bug from database.'
        return redirect('/todo')

@app.route('/update_list', methods=['POST'])
def update_list():
    update_list_name=request.form['update_list_name']
    list_id = int(request.form['list_id'])
    
    if len(update_list_name)<1:
        global alert_error, alert_color, alert_condition, alert_message
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Invalid List Name'
        alert_message = 'Null name not allowed'
        return redirect('/todo')
    list_check = List.query.filter_by(list_name=update_list_name).first()
    # print(type(list_check.list_id),type(list_id), '-----------------------------------')
    if list_check is not None and list_check.list_id != list_id:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'List Exists'
        alert_message = 'List name already exists, try another.'
        return redirect('/todo')

    list = List.query.get(list_id)
    list_desc=request.form['update_list_desc']
    try:
        list.list_name = update_list_name
        list.list_desc = list_desc
        db.session.commit()
        return redirect('/todo')
    except:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Server Error'
        alert_message = 'Got bug from database.'
        return redirect('/todo')

@app.route('/delete_list', methods=['POST'])
def delete_list():
    list_id = request.form['list_id']
    list = List.query.get(list_id)
    if list is None:
        global alert_error, alert_color, alert_condition, alert_message
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'List Not Exists'
        alert_message = 'List does not exists.'
        return redirect('/todo')
    account = Account.query.filter_by(email=email).first()
    print(account.lists)
    account.lists.remove(list)
    db.session.delete(list)
    db.session.commit()
    return redirect('/todo')

@app.route('/create_card', methods=['POST'])
def create_card():
    global alert_error, alert_color, alert_condition, alert_message

    card_title = request.form['card_title'].strip()
    if len(card_title)<1:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Invalid Card Title'
        alert_message = 'Card title can not be Null.'
        return redirect('/todo')

    card_deadline = request.form['card_deadline']
    now = datetime.now()
    current_datetime = datetime.isoformat(now)
    if card_deadline <= current_datetime:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Invalid Deadline'
        alert_message = 'Deadline must be in future.'
        return redirect('/todo')

    card_completed = request.form.get('card_completed') != None 
    if card_deadline > current_datetime and card_completed:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Invalid Input'
        alert_message = "Task can't be complete while creation."
        return redirect('/todo')

    card_list= request.form['card_list']
    list = List.query.filter_by(list_name=card_list).first()
    if list is None:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'List Not Exists'
        alert_message = 'Card must be in existing list.'
        return redirect('/todo')

    for card_temp in list.cards:
        if card_temp.title==card_title:
            alert_color = 'alert-danger'
            alert_error = True
            alert_condition = 'Card Name Exists'
            alert_message = 'Card must have unique name for the same list.'
            return redirect('/todo')

    card_content = request.form['card_content'].strip()
    try:
        card = Card(title=card_title, 
                    content=card_content, 
                    deadline=card_deadline, 
                    creation_datetime=current_datetime[:16], 
                    completed=card_completed
                    )
        db.session.add(card)
        list.cards.append(card)
        db.session.commit()
        return redirect('/todo')
    except:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Server Error'
        alert_message = 'Got bug from database.'
        return redirect('/todo')

@app.route('/delete_card', methods=['POST'])
def delete_card():
    global alert_error, alert_color, alert_condition, alert_message
    card_id = request.form['card_id']
    card = Card.query.get(card_id)
    if card is None:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Card Not Exists'
        alert_message = 'Card does not exists.'
        return redirect('/todo')
    list_id = request.form['list_id']
    list = List.query.get(list_id)
    if list is None:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'List Not Exists'
        alert_message = 'List does not exists.'
        return redirect('/todo')
    # print(list.cards, card, '-------------------------------------')
    list.cards.remove(card)
    db.session.delete(card)
    db.session.commit()
    return redirect('/todo')

@app.route('/update_card', methods=['POST'])
def update_card():
    global alert_error, alert_color, alert_condition, alert_message

    update_title=request.form['update_title'].strip()
    if len(update_title)<1:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Invalid Card Title'
        alert_message = 'Card title can not be Null.'
        return redirect('/todo')
    update_list= request.form['update_list']
    list = List.query.filter_by(list_name=update_list).first()
    if list is None:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'List Not Exists'
        alert_message = 'Card must be in existing list.'
        return redirect('/todo')

    card_id = request.form['card_id']
    past_list = List_Card.query.filter_by(card_id=card_id).first()
    list_card = List_Card.query.get((past_list.list_id,card_id))
    db.session.delete(list_card)
        
    for card_temp in list.cards:
        if card_temp.card_id!=card_id and card_temp.title==update_title:
            alert_color = 'alert-danger'
            alert_error = True
            alert_condition = 'Card Name Exists in'
            alert_message = f'Card must have unique name for the list {list.list_name}.'
            return redirect('/todo')
    # print(list_card)
    
    card = Card.query.get(card_id)
    update_deadline = request.form['update_deadline']
    if update_deadline<card.creation_datetime:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Invalid Deadline'
        alert_message = f'Update datetime must be after creation datetime i.e. {card.creation_datetime}'
        return redirect('/todo')


    update_completed = request.form.get('update_completed') != None 
    update_content = request.form['update_content']
    now = datetime.now()
    current_datetime = datetime.isoformat(now)
    try:
        card.title = update_title    
        card.content = update_content
        card.deadline = update_deadline
        card.completed = update_completed
        list.cards.append(card)
        card.last_update = current_datetime[:16]
        if update_completed:
            card.completed_datetime = current_datetime[:16]
        db.session.commit()
        return redirect('/todo')
    except:
        db.session.rollback()
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Server Error'
        alert_message = 'Got bug from database.'
        return redirect('/todo')

@app.route("/summary", methods=['GET'])
def summary():
    return render_template('summary.html')

import re
@app.route("/signup", methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        signup_name=request.form['name'].strip()
        signup_email=request.form['email']
        password=request.form['password']
        confirm_password=request.form['confirm_password']
        condition, error_message, error = 'Congrats','Your account is made successfully.',False
        special_char_name=re.compile('[@!$%^&*().<>?/\|}{~:]#0123456789')
        
        res = len([ele for ele in signup_name if ele.isalpha()])
        if special_char_name.search(signup_name) != None or res<1:
            error = True
            condition = 'Invalid Name'
            error_message = 'Only alphabates and space allowed.'
        elif '@' not in signup_email or len(signup_email)<3:
            error = True
            condition = 'Invalid Email'
            error_message = 'Please enter a valid Email.(Only [A-Z],[a-z],<space>,<_>,[0-9],@ allowed)'
        elif password != confirm_password:
            error = True
            condition = 'Invalid Password'
            error_message = 'Please enter both of your passwords again.'
        else:
            account = Account.query.filter_by(email=signup_email).first()
            # peter = User.query.filter_by(username='peter').first()
            if account != None:
                error = True
                condition = 'Email Already Exists'
                error_message = 'Please provide another email.'
        if error:
            return render_template('signUp.html', show=True, color='alert-danger', condition=condition, error_message=error_message, name=signup_name,  email=signup_email)
        try:
            account = Account(password=password, name=signup_name, email=signup_email)
            db.session.add(account)
            db.session.commit()
        except:
            error = True
            condition = 'Error'
            error_message = 'Server error.'                        

        global signedin, email, name
        signedin = True
        email = signup_email
        name = signup_name
        return redirect('/home')
        
    if request.method == 'GET':
        return render_template('signUp.html')

@app.route("/signin", methods=['POST'])
def signin():
    check_email=request.form['email']
    password = request.form['password']
    account = Account.query.filter_by(email=check_email).first()
    global alert_error, alert_color, alert_condition, alert_message
    print(account,'--------------------------------------------------')
    if request.method == 'POST':
        if account is None:
            alert_error = True
            alert_condition = 'Email Not Exists'
            alert_message = 'Please provide another email.'
        elif '@' not in check_email or len(check_email)<3:
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

        global signedin, name, email
        signedin = True
        name = account.name
        email = account.email
        return redirect('/home')

@app.route('/logout', methods=['GET'])
def logout():
    global signedin, name, email
    signedin = False
    name = ''
    email = ''
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

# CREATE TABLE "card" (
# 	"card_id"	INTEGER,
# 	"title"	TEXT NOT NULL,
# 	"content"	TEXT,
# 	"deadline"	NUMERIC NOT NULL,
# 	"completed"	INTEGER NOT NULL DEFAULT 0,
# 	PRIMARY KEY("card_id" AUTOINCREMENT)
# );
    
    # print('''
    #     card_title: {},
    #     card_content: {},
    #     card_deadline: {},
    #     card_list: {},
    #     card_completed: {}
    # '''.format(card_title, card_content, card_deadline, card_list, card_completed))
    # return redirect('/todo')
        # card_completed: {}, card_completed
