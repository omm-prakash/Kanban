from .database import db
from application.models import *
from application.validation import *
from flask_restful import fields, marshal_with, Resource, reqparse
from application.controllers import present_time, update_stat_delete

def update_stat_count(card,list,user,completed):
    if completed:
        if not card.completed:
            list.lcompleted+=1
            user.tcompleted+=1
            list.lpending-=1
            user.tpending-=1
    else:
        if card.completed:
            list.lpending+=1
            user.tpending+=1
            list.lcompleted-=1
            user.tcompleted-=1

# CREATE TABLE "list" (
# 	"list_id"	INTEGER,
# 	"list_name"	TEXT NOT NULL,
# 	"list_desc"	TEXT,
# 	"lpending"	INTEGER DEFAULT 0,
# 	"lcompleted"	INTEGER DEFAULT 0,
# 	"loverdue"	INTEGER DEFAULT 0,
# 	PRIMARY KEY("list_id" AUTOINCREMENT)
# );

list_output={
    'list_id': fields.Integer,
    'list_name': fields.String,
    'list_desc': fields.String,
    'lpending': fields.Integer,
    'lcompleted': fields.Integer,
    'loverdue': fields.Integer
}
list_parser = reqparse.RequestParser()
list_parser.add_argument('list_name')
list_parser.add_argument('list_desc')
# list_parser = reqparse.RequestParser()
# list_parser.add_argument('title')
# list_parser.add_argument('content')

class ListApi(Resource):
    @marshal_with(list_output)
    def get(self,email,list_name):
        account=Account.query.filter_by(email=email).first()
        if account:
            lists=account.lists
            for list in lists:
                if list.list_name==list_name:
                    return list, 200
            raise NotFoundError('List does not exists',404)
        else:
            raise NotFoundError('Account does not exists',404)

    @marshal_with(list_output)
    def put(self,email,list_name):
        account=Account.query.filter_by(email=email).first()
        args = list_parser.parse_args()
        update_list_name = args.get("list_name", None)
        update_list_desc = args.get("list_desc", None)
        print(update_list_desc,update_list_name)
        if account:
            if len(update_list_name)<1:
                raise BusinessValidationError("List name can't not be Null.",'Invalid Name',400) 
            name_exist = len([list for list in account.lists if list.list_name==update_list_name])>0 and list_name != update_list_name
            
            if name_exist:
                raise DuplicationError('Update List Name already exists',409) 
            for list in account.lists:
                if list.list_name==list_name:
                    try:
                        list.list_name = update_list_name
                        list.list_desc = update_list_desc
                        db.session.commit()
                        return list,200                
                    except:
                        return ServerError('Error from List Table')
                    break
            raise NotFoundError('List does not exists',404)
        else:
            raise NotFoundError('Account does not exists',404)

    def delete(self,email,list_name):
        account=Account.query.filter_by(email=email).first()
        if account:
            lists=account.lists
            for list in lists:
                if list.list_name==list_name:
                    cards=list.cards
                    try:
                        for card in cards:
                            update_stat_delete(card, list, account)
                            list.cards.remove(card)
                            db.session.delete(card)

                        account.lists.remove(list)
                        db.session.delete(list)
                        db.session.commit()
                        return 'Successfully Deleted',200
                    except:
                        return ServerError('Error from List Table')
            raise NotFoundError('List does not exists',404)
        else:
            raise NotFoundError('Account does not exists',404)

    @marshal_with(list_output)
    def post(self,email):
        account=Account.query.filter_by(email=email).first()
        args = list_parser.parse_args()
        list_name = args.get("list_name")
        list_desc = args.get("list_desc")
        print(list_name,list_desc)
        # print(account)
        if account:
            name_exist = len([list for list in account.lists if list.list_name==list_name])>0  
            if name_exist:
                raise DuplicationError('List Name already exists',409) 
            if len(list_name)<1:
                raise BusinessValidationError("List name can't not be Null.",'Invalid Name',400) 
            if len(account.lists)>=5:
                raise BusinessValidationError('Total number of lists can not more than Five.','List Limit Exceeds',400) 
            list = List(list_name=list_name, list_desc=list_desc)
            try:
                db.session.add(list)
                account.lists.append(list)
                db.session.commit()
                return list,201
            except:
                return ServerError('Error from List Table')
        else:
            raise BusinessValidationError('Account does not exists','404',400)

card_output={
    'card_id': fields.Integer,
    'title': fields.String,
    'content': fields.String,
    'deadline': fields.String,
    'creation_datetime': fields.String,
    'completed': fields.Boolean,
    'completed_datetime': fields.String,
    'last_update': fields.String
}
card_parser = reqparse.RequestParser()
card_parser.add_argument('title')
card_parser.add_argument('content')
card_parser.add_argument('deadline')
card_parser.add_argument('completed')
card_parser.add_argument('email')

# CREATE TABLE "card" (
# 	"card_id"	INTEGER,
# 	"title"	TEXT NOT NULL,
# 	"content"	TEXT,
# 	"deadline"	TEXT NOT NULL,
# 	"creation_datetime"	TEXT NOT NULL,
# 	"completed"	INTEGER DEFAULT 0,
# 	"completed_datetime"	TEXT,
# 	"last_update"	TEXT,
# 	PRIMARY KEY("card_id" AUTOINCREMENT)
# );

class CardApi(Resource):
    @marshal_with(card_output)
    def get(self,list_id,card_name):
        card_name=card_name.strip()
        list=List.query.get(list_id)
        if list:
            cards=list.cards
            for card in cards:
                if card.title==card_name:
                    return card, 200
            raise NotFoundError('Card does not exists',404)
        else:
            raise NotFoundError('List does not exists',404)
        
    @marshal_with(card_output)
    def put(self,list_id,card_name):
        args = card_parser.parse_args()
        title = args.get("title", None).strip()
        content = args.get("content", None).strip()
        deadline = args.get("deadline", None).strip()
        completed = args.get("completed",None)
        email=args.get('email', None)
        list=List.query.get(list_id)
        # print(completed)
        print('''
            title: {},
            content: {},
            deadline: {},
            creation_datetime: {},
            completed: {},
            last_update: {}
        '''.format(title,content,deadline,present_time()[:16],completed,present_time()[:16]))
        if completed=='False':
            completed=False
        else:
            completed=True
        if list:
            user=Account.query.filter_by(email=email).first()
            if user:
                if list not in user.lists:
                    raise BusinessValidationError('Account does not have list {}'.format(list.list_name),'404',400)
            else:
                raise BusinessValidationError('Account does not exists','404',400)
            if len(title)<1:
                raise BusinessValidationError("Card name can't not be Null.",'Invalid Name',400) 
            
            for card in list.cards:
                print(card.title)
                if card.title==card_name:
                    try:
                        if deadline<card.creation_datetime:
                            raise BusinessValidationError(f'Update datetime must be after creation datetime i.e. {card.creation_datetime}','Invalid Deadline',400) 
                        name_exist = len([card for card in list.cards if card.title==title])>0 and card_name != title
                        if name_exist:
                            raise BusinessValidationError(f'Card must have unique name for the selected list i.e. {list.list_name}.','Card Name Exists',400) 

                        update_stat_count(card,list,user,completed)
                        card.title = title    
                        card.content = content
                        card.deadline = deadline
                        card.completed = completed
                        list.cards.append(card)
                        card.last_update = present_time()[:16]
                        if completed:
                            card.completed_datetime = present_time()[:16]
                        print(card.title,'-------------------------------------')
                        db.session.commit()
                        return card,200                
                    except:
                        return ServerError('Error from Card Table')
                    break
            raise NotFoundError(f'Card does not exists in list id: {list_id}',404)
            
        else:
            raise NotFoundError('List does not exists',404)

    def delete(self,email,list_id,card_name):
        list=List.query.get(list_id)
        user=Account.query.filter_by(email=email).first()
        # print(list,card)
        if list:
            if user:
                if list not in user.lists:
                    raise BusinessValidationError('Account does not have list {}'.format(list.list_name),'404',400)
                cards=list.cards
                for card in cards:
                    if card.title==card_name:
                        try:
                            list.cards.remove(card)
                            update_stat_delete(card, list, user)
                            db.session.delete(card)
                            db.session.commit()
                            return 'Successfully Deleted',200
                        except:
                            return ServerError('Error from List Table')
                raise NotFoundError('Card does not exists',404)
            else:
                raise BusinessValidationError('Account does not exists','404',400)
        else:
            raise NotFoundError('List does not exists',404)

    @marshal_with(card_output)
    def post(self,list_id):
        args = card_parser.parse_args()
        title = args.get("title", None).strip()
        content = args.get("content", None).strip()
        deadline = args.get("deadline", None).strip()
        completed = args.get("completed",None)
        email=args.get('email', None)
        list=List.query.get(list_id)
        if list:
            user=Account.query.filter_by(email=email).first()
            if user:
                if list not in user.lists:
                    raise BusinessValidationError('Account does not have list {}'.format(list.list_name),'404',400)
            else:
                raise BusinessValidationError('Account does not exists','404',400)
            name_exist = len([card for card in list.cards if card.title==title])>0  
            if name_exist:
                raise DuplicationError('Card Name already exists',409) 
            if len(title)<1:
                raise BusinessValidationError("Card title can not be Null.",'Invalid Card Title',400) 
            if deadline <= present_time():
                raise BusinessValidationError("Deadline must be in future.",'Invalid Deadline',400)
            if completed=='True':
                raise BusinessValidationError("Task can't be complete while creation.",'Invalid Input',400)  
            # print(type(completed))
            card = Card(title=title,
                        content=content,
                        deadline=deadline,
                        creation_datetime=present_time()[:16],
                        completed=False,
                        last_update=present_time()[:16]
                    )
            try:
                db.session.add(card)
                # print(list,'--------------------')
                list.cards.append(card)
                # print(card,'----------------------------------')   
                list.lpending += 1
                user.tpending += 1
                db.session.commit()
                return card,201
            except:
                return ServerError('Error from Card Table')
        else:
            raise NotFoundError('List does not exists',404)

class SummaryApi(Resource):
    def get(self,email):
        current_user=Account.query.filter_by(email=email).first()
        lists,overdue_count=[],0
        if current_user:
            lists = current_user.lists
            summary = []
            for list in lists:
                complition_date, data = {}, {}
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
                data['list_name']=list.list_name
                data['trendline']=complition_date
                data['Pendings']=list.lpending
                data['Completed']=list.lcompleted                
                data['Over_Due']=overdue_count
                
                db.session.commit()
                summary.append(data)
            return summary, 200
        else:
            raise BusinessValidationError('Account does not exists','404',400)

