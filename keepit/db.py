import mysql.connector
from flask import g

def get_db():
	db = mysql.connector.connect(user='root', password='admin',host='127.0.0.1',port='3306',database='keepit')
	return db

def close_db(e=None):
	db = g.pop('db', None)

	if db is not None:
		db.close()

'''
keepit.usuario clue
+------------+-------------+------+-----+---------+----------------+
| Field      | Type        | Null | Key | Default | Extra          |
+------------+-------------+------+-----+---------+----------------+
| id_usuario | int(11)     | NO   | PRI | NULL    | auto_increment |
| fnome      | varchar(45) | NO   |     | NULL    |                |
| lnome      | varchar(45) | NO   |     | NULL    |                |
| nascimento | date        | NO   |     | NULL    |                |
| login      | varchar(45) | NO   |     | NULL    |                |
| senha      | varchar(45) | NO   |     | NULL    |                |
+------------+-------------+------+-----+---------+----------------+
'''
def insert_user(data: dict):
	db = get_db()
	cursor = db.cursor(dictionary=True)

	insert_user = ('INSERT INTO keepit.usuario (fnome, lnome, nascimento, login, senha) VALUES (%s, %s, %s, %s, %s)')
	data_user = (data['fname'], data['lname'], data['born'], data['username'], data['password'])
	cursor.execute(insert_user,data_user)
	db.commit()
	cursor.close()
	db.close()

def check_login(login: str):
	db = get_db()
	cursor = db.cursor(dictionary=True)

	select_user = ('SELECT * FROM keepit.usuario WHERE login = %s')
	data_user = (login,)
	cursor.execute(select_user,data_user)
	user = cursor.fetchone()
	cursor.close()
	db.close()

	return user

def select_user_by_id(id: int):
	db = get_db()
	cursor = db.cursor(dictionary=True)
	
	select_user = ('SELECT * FROM keepit.usuario WHERE id_usuario = %s')
	data_user = (id,)
	cursor.execute(select_user,data_user)
	user = cursor.fetchone()
	cursor.close()
	db.close()

	return user

def select_user_by_credentials(username: str, password: str):
	db = get_db()
	cursor = db.cursor(dictionary=True)

	select_user = ('SELECT * FROM keepit.usuario WHERE login = %s AND senha = %s')
	data_user = (username,password)
	cursor.execute(select_user,data_user)
	user = cursor.fetchone()
	cursor.close()
	db.close()

	return user


''' 
keepit.recurso clue
+-------------------+-------------+------+-----+---------+----------------+
| Field             | Type        | Null | Key | Default | Extra          |
+-------------------+-------------+------+-----+---------+----------------+
| id_recurso        | int(11)     | NO   | PRI | NULL    | auto_increment |
| id_usuario        | int(11)     | NO   | PRI | NULL    |                |
| valor             | int(11)     | NO   |     | NULL    |                |
| data_pagamento    | date        | NO   |     | NULL    |                |
| nome              | varchar(45) | NO   |     | NULL    |                |
| data_cancelamento | date        | NO   |     | NULL    |                |
| data_anotacao     | date        | NO   |     | NULL    |                |
+-------------------+-------------+------+-----+---------+----------------+

keepit.despesa clue
+------------+---------+------+-----+---------+----------------+
| Field      | Type    | Null | Key | Default | Extra          |
+------------+---------+------+-----+---------+----------------+
| id_despesa | int(11) | NO   | PRI | NULL    | auto_increment |
| id_recurso | int(11) | NO   | MUL | NULL    |                |
+------------+---------+------+-----+---------+----------------+
 
keepit.despesa_comum clue
+------------+------------+------+-----+---------+-------+
| Field      | Type       | Null | Key | Default | Extra |
+------------+------------+------+-----+---------+-------+
| id_despesa | int(11)    | NO   | PRI | NULL    |       |
| constante  | tinyint(1) | NO   |     | NULL    |       |
| automatica | tinyint(1) | NO   |     | NULL    |       |
| dia_mes    | int(11)    | NO   |     | NULL    |       |
| status     | tinyint(1) | NO   |     | NULL    |       |
+------------+------------+------+-----+---------+-------+
'''
def insert_expense_common(id_user: int, data: dict):
	'''
	The dictionary has to be as shown below:
	{
		'value': 0,
		'payment_date': 'dd/mm/yyyy',
		'name': 'abc',
		'cancelation_date': 'dd/mm/yyyy',
		'anotation_date': 'dd/mm/yyyy',
		'constant': 0,
		'automatic': 0,
		'month_day': 0,
		'status': 0
	}
	'''
	db = get_db()
	cursor = db.cursor(dictionary=True)

	insert_query = ('INSERT INTO keepit.recurso (id_usuario, valor, data_pagamento, nome, data_cancelamento, data_anotacao)'
						+ 'VALUES (%s, %s, %s, %s, %s, %s)')
	data_insert = (id_user,data['value'],data['payment_date'],data['name'],data['cancelation_date'],data['anotation_date'])
	cursor.execute(insert_query,data_insert)
	id_resource = cursor.lastrowid

	insert_query = ('INSERT INTO keepit.despesa (id_recurso)'
						+ 'VALUES (%s)')
	data_insert = (id_resource,)
	cursor.execute(insert_query,data_insert)
	id_expense = cursor.lastrowid
	
	insert_query = ('INSERT INTO keepit.despesa_comum (id_despesa, constante, automatica, dia_mes, status)'
						+ 'VALUES (%s, %s, %s, %s, %s)')
	data_insert = (id_expense,data['constant'],data['automatic'],data['month_day'],data['status'])
	cursor.execute(insert_query,data_insert)
	db.commit()
	cursor.close()
	db.close()

def select_expense_common(id_user: int):
	db = get_db()
	cursor = db.cursor(dictionary=True)

	select_query = ('SELECT * FROM'
		+ '((keepit.recurso JOIN keepit.despesa ON keepit.recurso.id_recurso=keepit.despesa.id_recurso)'
		+ 'JOIN keepit.despesa_comum ON keepit.despesa.id_despesa=keepit.despesa_comum.id_despesa)'
		+ 'WHERE keepit.recurso.id_usuario=%s ORDER BY keepit.recurso.data_anotacao DESC')
	select_data = (id_user,)
	cursor.execute(select_query,select_data)
	results = cursor.fetchall()
	cursor.close()
	db.close()

	return results

''' 
keepit.despesa_incomum clue
+--------------------+-------------+------+-----+---------+-------+
| Field              | Type        | Null | Key | Default | Extra |
+--------------------+-------------+------+-----+---------+-------+
| despesa_id_despesa | int(11)     | NO   | PRI | NULL    |       |
| destino            | varchar(45) | NO   |     | NULL    |       |
+--------------------+-------------+------+-----+---------+-------+
'''
def insert_expense_uncommon(id_user: int, data: dict):
	'''
	The dictionary has to be as shown below:

	'''

''' 
keepit.despesa_estimada clue

'''
def insert_expense_estimated(id_user: int, data: dict):
	'''
	The dictionary has to be as shown below:

	'''

''' 
keepit.despesa_programada clue

'''
def insert_expense_programmed(id_user: int, data: dict):
	'''
	The dictionary has to be as shown below:

	'''

''' 
keepit.receita clue

'''
def insert_revenues(id_user: int, data: dict):
	'''
	The dictionary has to be as shown below:

	'''

''' 
keepit.receita_comum clue

'''
def insert_revenues_common(id_user: int, data: dict):
	'''
	The dictionary has to be as shown below:

	'''

''' 
keepit.receita_incomum clue

'''
def insert_revenues_uncommon(id_user: int, data: dict):
	'''
	The dictionary has to be as shown below:

	'''

def remove_resource(id_resource: int):
	db = get_db()
	cursor = db.cursor(dictionary=True)
	delete_query = ('DELETE FROM keepit.recurso WHERE keepit.recurso.id_recurso = %s')
	delete_data = (id_resource,)
	cursor.execute(delete_query,delete_data)
	db.commit()
	cursor.close()
	db.close()