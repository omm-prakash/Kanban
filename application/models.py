from enum import unique
from .database import db

class Account(db.Model):
    __tablename__ = 'account'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    password = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    lists = db.relationship('List', secondary="account_list")

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
    deadline = db.Column(db.Integer, nullable=False)
    completed = db.Column(db.Integer, nullable=False, default=0)

# CREATE TABLE "card" (
# 	"card_id"	INTEGER,
# 	"title"	TEXT NOT NULL,
# 	"content"	TEXT,
# 	"deadline"	NUMERIC NOT NULL,
# 	"completed"	INTEGER NOT NULL DEFAULT 0,
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



# class User(db.Model):
#     __tablename__ = 'user'
#     user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     username = db.Column(db.String, unique=True)
#     email = db.Column(db.String, unique=True)

# class Article(db.Model):
#     __tablename__ = 'article'
#     article_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     title = db.Column(db.String)
#     content = db.Column(db.String)
#     authors = db.relationship("User", secondary="article_authors")

# class ArticleAuthors(db.Model):
#     __tablename__ = 'article_authors'
#     user_id = db.Column(db.Integer,   db.ForeignKey("user.user_id"), primary_key=True, nullable=False)
#     article_id = db.Column(db.Integer,  db.ForeignKey("article.article_id"), primary_key=True, nullable=False) 
