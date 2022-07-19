import os
import glob
from crypt import methods
from .database import db
from flask import redirect, request
from flask import render_template
from flask import current_app as app
from datetime import datetime
from flask_security import login_required, roles_accepted, roles_required, current_user
from application.models import *
import matplotlib.pyplot as plt
def present_time():
    now = datetime.now()
    present_datetime = datetime.isoformat(now)[:16]
    return present_datetime

def update_stat_delete(card,list,user):
    if card.completed:
        list.lcompleted-=1
        user.tcompleted-=1
    else:
        list.lpending-=1
        user.tpending-=1

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
        role = Role.query.get(2)
        if role not in user.roles:
            user.roles.append(role)
        db.session.commit()
    files = glob.glob('./static/plots/*')
    for f in files:
        os.remove(f)    
    return render_template('index.html')

@app.route("/board", methods=['GET'])
def board():
    global alert_error, alert_color, alert_condition, alert_message
    lists = []
    if current_user.is_authenticated:
        lists = current_user.lists
    if alert_error:
        alert_error = False
        template = render_template('board.html',show=True, alert_color=alert_color, alert_condition=alert_condition, alert_message=alert_message, lists=lists)
        alert_color, alert_condition, alert_message = '','',''
        return template
    return render_template('board.html', lists=lists)

@app.route('/create_list', methods=['POST'])
@login_required
def create_list():
    global alert_error, alert_color, alert_condition, alert_message, email
    list_name = request.form['list_name'].strip()
    list_desc=request.form['list_desc'].strip()
    name_exist = len([list for list in current_user.lists if list.list_name==list_name])>0
    if name_exist:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'List Exists'
        alert_message = 'List name already exists, try another.'
        return redirect('/board')
    if len(list_name)<1:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Invalid Name'
        alert_message = 'List name cant not be Null.'
        return redirect('/board')
    if len(current_user.lists)>=5:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'List Limit Exceeds'
        alert_message = 'Total number of lists can not more than Five.'
        return redirect('/board')
    try:
        list = List(list_name=list_name, list_desc=list_desc)
        db.session.add(list)
        current_user.lists.append(list)
        db.session.commit()
        return redirect('/board')
    except:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Server Error'
        alert_message = 'Got bug from database.'
        return redirect('/board')

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
        return redirect('/board')
    # list_check = List.query.filter_by(list_name=update_list_name).first()
    name_exist = len([list for list in current_user.lists if list.list_name==update_list_name])>1
    if name_exist:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'List Exists'
        alert_message = 'List name already exists, try another.'
        return redirect('/board')

    list = List.query.get(list_id)
    list_desc=request.form['update_list_desc']
    try:
        list.list_name = update_list_name
        list.list_desc = list_desc
        db.session.commit()
        return redirect('/board')
    except:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Server Error'
        alert_message = 'Got bug from database.'
        return redirect('/board')

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
        return redirect('/board')
    for card in list.cards:
        update_stat_delete(card, list, current_user)

    current_user.lists.remove(list)
    db.session.delete(list)
    db.session.commit()
    return redirect('/board')

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
        return redirect('/board')

    card_deadline = request.form['card_deadline']
    if card_deadline <= present_time():
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Invalid Deadline'
        alert_message = 'Deadline must be in future.'
        return redirect('/board')

    card_completed = request.form.get('card_completed') != None 
    if card_deadline > present_time() and card_completed:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Invalid Input'
        alert_message = "Task can't be complete while creation."
        return redirect('/board')

    card_list= request.form['card_list']
    list = None
    for lst in current_user.lists:
        if lst.list_name==card_list:
            list=lst
            break
    if list is None:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'List Not Exists'
        alert_message = 'Card must be in existing lists.'
        return redirect('/board')

    for card_temp in list.cards:
        if card_temp.title==card_title:
            alert_color = 'alert-danger'
            alert_error = True
            alert_condition = 'Card Name Exists'
            alert_message = f'Card must have unique name for {list.list_name}'
            return redirect('/board')

    card_content = request.form['card_content'].strip()
    try:
        card = Card(title=card_title, 
                    content=card_content, 
                    deadline=card_deadline, 
                    creation_datetime=present_time()[:16], 
                    completed=card_completed,
                    last_update=present_time()[:16]
                    )
        db.session.add(card)
        list.cards.append(card)
        list.lpending += 1
        current_user.tpending += 1
        db.session.commit()
        return redirect('/board')
    except:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Server Error'
        alert_message = 'Got bug from database.'
        return redirect('/board')

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
        return redirect('/board')
    list_id = request.form['list_id']
    list = List.query.get(list_id)
    if list is None:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'List Not Exists'
        alert_message = 'List does not exists.'
        return redirect('/board')
    list.cards.remove(card)
    update_stat_delete(card,list,current_user)
    db.session.delete(card)
    db.session.commit()
    return redirect('/board')

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
        return redirect('/board')
    update_list= request.form['update_list']
    # list = List.query.filter_by(list_name=update_list).first()
    list = None
    for lst in current_user.lists:
        if lst.list_name==update_list:
            list=lst
            break

    if list is None:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'List Not Exists'
        alert_message = 'Card must be in existing list.'
        return redirect('/board')

    card_id = request.form['card_id']
    card = Card.query.get(card_id)
    past_list = List_Card.query.filter_by(card_id=card_id).first()
    lst = List.query.get(past_list.list_id)
    update_stat_delete(card,lst,current_user)
    # list_card = List_Card.query.get((past_list.list_id,card_id))
    db.session.delete(past_list)
        
    for card_temp in list.cards:
        if card_temp.card_id!=card_id and card_temp.title==update_title:
            alert_color = 'alert-danger'
            alert_error = True
            alert_condition = 'Card Name Exists in'
            alert_message = f'Card must have unique name for the selected list i.e. {list.list_name}.'
            return redirect('/board')
    # print(list_card)
    
    update_completed = request.form.get('update_completed') != None 
    update_deadline = request.form['update_deadline']
    if update_deadline<card.creation_datetime:
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Invalid Deadline'
        alert_message = f'Update datetime must be after creation datetime i.e. {card.creation_datetime}'
        return redirect('/board')
    
    if update_completed:
        list.lcompleted+=1
        current_user.tcompleted+=1
    else:
        list.lpending+=1
        current_user.tpending+=1

    update_content = request.form['update_content']
    try:
        card.title = update_title    
        card.content = update_content
        card.deadline = update_deadline
        card.completed = update_completed
        list.cards.append(card)
        card.last_update = present_time()[:16]
        if update_completed:
            card.completed_datetime = present_time()[:16]
        db.session.commit()
        return redirect('/board')
    except:
        db.session.rollback()
        alert_color = 'alert-danger'
        alert_error = True
        alert_condition = 'Server Error'
        alert_message = 'Got bug from database.'
        return redirect('/board')

@app.route("/summary", methods=['GET'])
def summary():
    lists=[]
    if current_user.is_authenticated:
        lists = current_user.lists
        keys = ['Pendings', 'Completed']
        for list in lists:
            complition_date = {}
            overdue_count=0
            for card in list.cards:
                if card.deadline<present_time() and not card.completed:
                    overdue_count+=1
                date=card.completed_datetime
                if date is not None:
                    date=date[:10]
                    if date not in complition_date.keys():
                        complition_date[date] = 1
                    else:
                        complition_date[date]+=1
                date=card.last_update
                     
            list.loverdue = overdue_count

            dates = complition_date.keys()
            counts = complition_date.values()
            n=len(counts)
            if n>0:
                yticks=range(0,max(counts)+1)
            else:
                yticks=range(0,2)
            plt.figure(facecolor='#ffd9b8')
            plt.grid(axis='y')
            plt.plot(dates,counts,'bo-')
            plt.ylabel('Card Count')
            plt.xlabel('Date')
            plt.yticks(yticks)
            plt.savefig(f'./static/plots/trend_{list.list_id}.png')
            plt.clf()

            values=[list.lpending, list.lcompleted]
            n=len(values)
            if n>0:
                yticks=range(0,max(values)+2)
            else:
                yticks=range(0,2)
            plt.bar(keys,values)
            plt.ylabel('Count')
            plt.xlabel('Task')
            plt.yticks(yticks)
            plt.savefig(f'./static/plots/list_{list.list_id}.png')
            plt.clf()
            db.session.commit()
    
    return render_template('summary.html',lists=lists,overdue=overdue_count)

            # print('list ID: {}, list name: {}, list pending: {}, list completed: {}'.format(list.list_id,list.list_name,list.lpending,list.lcompleted))
            # print(values)
