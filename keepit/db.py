import mysql.connector
from flask import g

def get_db():
	if 'db' not in g:
		g.db = mysql.connector.connect(user='root', password='admin',host='127.0.0.1',port='3306',database='keepit')
	return g.db

def close_db(e=None):
	db = g.pop('db', None)

	if db is not None:
		db.close()

