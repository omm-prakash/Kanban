from crypt import methods
from .database import db
from flask import redirect, request
from flask import render_template
from flask import current_app as app
from datetime import datetime
from flask_security import login_required, roles_accepted, roles_required, current_user
from application.models import *

alert_error, alert_color, alert_condition, alert_message = False,'','',''
# signedin,name,email = False,'',''
@app.route("/home", methods=['GET'])
def home():
    return render_template('index.html')

@app.route("/", methods=['GET'])
def main():
    if current_user.is_authenticated:
        id = current_user.id
        user = Account.query.get(id)
        if current_user.username is None:
            user.username = current_user.email.rpartition('@')[0]
        # role_check = roles_users.query.filter_by(user_id=id).all() is not None
        role = Role.query.get(2)
        if role not in user.roles:
            user.roles.append(role)
        db.session.commit()
    return render_template('index.html')

@app.route("/todo", methods=['GET'])
def todo():
    global alert_error, alert_color, alert_condition, alert_message
    lists = []
    if current_user.is_authenticated:
        lists = current_user.lists
    if alert_error:
        alert_error = False
        template = render_template('todo.html',show=True, alert_color=alert_color, alert_condition=alert_condition, alert_message=alert_message, lists=lists)
        alert_color, alert_condition, alert_message = '','',''
        return template
    return render_template('todo.html', lists=lists)

@app.route('/create_list', methods=['POST'])
@login_required
def create_list():
    global alert_error, alert_color, alert_condition, alert_message, email
    list_name = request.form['list_name'].strip()
    list_desc=request.form['list_desc'].strip()
    name_exist = List.query.filter_by(list_name=list_name).first() is not None
    if name_exist:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'List Exists'
        alert_message = 'List name already exists, try another.'
        return redirect('/todo')
    if len(list_name)<1:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Invalid Name'
        alert_message = 'List name cant not be Null.'
        return redirect('/todo')
    try:
        list = List(list_name=list_name, list_desc=list_desc)
        db.session.add(list)
        current_user.lists.append(list)
        db.session.commit()
        return redirect('/todo')
    except:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Server Error'
        alert_message = 'Got bug from database.'
        return redirect('/todo')

@app.route('/update_list', methods=['POST'])
@login_required
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
@login_required
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
    current_user.lists.remove(list)
    db.session.delete(list)
    db.session.commit()
    return redirect('/todo')

@app.route('/create_card', methods=['POST'])
@login_required
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
@login_required
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
@login_required
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
            alert_message = f'Card must have unique name for the selected list i.e. {list.list_name}.'
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

