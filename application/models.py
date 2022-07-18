from .database import db
from flask_security import UserMixin, RoleMixin
from flask_login import login_manager

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('account.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))    

class Account(db.Model, UserMixin):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    password = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    active = db.Column(db.Boolean())
    lists = db.relationship('List', secondary="account_list")
    roles = db.relationship('Role', secondary=roles_users,backref=db.backref('users', lazy='dynamic'))

class Role(db.Model, RoleMixin):
    __tablename__ = 'role'
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

# CREATE TABLE "account" (
# 	"id"	INTEGER,
# 	"password"	TEXT NOT NULL,
# 	"name"	TEXT NOT NULL,
# 	"email"	TEXT NOT NULL UNIQUE,
# 	PRIMARY KEY("id" AUTOINCREMENT)
# );

class List(db.Model):
    __tablename__ = 'list'
    list_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    list_name = db.Column(db.String, nullable=False)
    list_desc = db.Column(db.String)
    cards = db.relationship('Card', secondary="list_card")

# CREATE TABLE "list" (
# 	"list_id"	INTEGER,
# 	"list_name"	TEXT NOT NULL,
# 	"list_desc"	TEXT,
# 	PRIMARY KEY("list_id" AUTOINCREMENT)
# );

class Account_List(db.Model):
    __tablename__ = 'account_list'
    id = db.Column(db.Integer, db.ForeignKey("account.id"), primary_key=True, nullable=False)
    list_id = db.Column(db.Integer, db.ForeignKey("list.list_id"), primary_key=True, nullable=False)

# CREATE TABLE "account_list" (
# 	"id"	INTEGER NOT NULL,
# 	"list_id"	INTEGER NOT NULL,
# 	FOREIGN KEY("id") REFERENCES "account"("id"),
# 	FOREIGN KEY("list_id") REFERENCES "list"("list_id"),
# 	PRIMARY KEY("id","list_id")
# );

class Card(db.Model):
    __tablename__ = 'card'
    card_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String)
    deadline = db.Column(db.String, nullable=False)
    creation_datetime = db.Column(db.String, nullable=False)
    completed = db.Column(db.Boolean(), default=0)
    last_update = db.Column(db.String)
    completed_datetime = db.Column(db.String)

# CREATE TABLE "card" (
# 	"card_id"	INTEGER,
# 	"title"	TEXT NOT NULL,
# 	"content"	TEXT,
# 	"deadline"	TEXT NOT NULL,
#   "creation_datetime" TEXT NOT NULL,
# 	"completed"	INTEGER NOT NULL DEFAULT 0,
#   "completed_datetime" TEXT,
#   "last_update" TEXT,
# 	PRIMARY KEY("card_id" AUTOINCREMENT)
# );

class List_Card(db.Model):
    __tablename__ = 'list_card'
    list_id = db.Column(db.Integer, db.ForeignKey('list.list_id'), primary_key=True, nullable=False)
    card_id = db.Column(db.Integer, db.ForeignKey('card.card_id'), primary_key=True, nullable=False)

# CREATE TABLE "list_card" (
# 	"list_id"	INTEGER NOT NULL,
# 	"card_id"	INTEGER NOT NULL,
# 	FOREIGN KEY("list_id") REFERENCES "list"("list_id"),
# 	FOREIGN KEY("card_id") REFERENCES "card"("card_id"),
# 	PRIMARY KEY("list_id","card_id")
#   );

