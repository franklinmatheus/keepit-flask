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
| data_anotacao     | varchar(45) | NO   |     | NULL    |                |
+-------------------+-------------+------+-----+---------+----------------+
'''
def insert_resource(id_user: int, data: dict):
	'''
	The dictionary has to be as shown below:
	{
		'value': 0,
		'payment_date': 'dd/mm/yyyy',
		'name': 'abc',
		'cancelation_date': 'dd/mm/yyyy',
		'anotation_date': 'dd/mm/yyyy'
	}
	'''
	db = get_db()
	cursor = db.cursor(dictionary=True)
	insert_query = ('INSERT INTO keepit.usuario (id_usuario, valor, data_pagamento, nome, data_cancelamento, data_anotacao)'
						+ 'VALUES (%s, %s, %s, %s, %s)')
	data_insert = (id_user,data['value'],data['payment_date'],data['name'],data['cancelation_date'],data['anotation_date'])
	cursor.execute(data_insert,insert_query)
	db.commit()
	cursor.close()
	db.close()


''' 
keepit.despesa clue
+------------+---------+------+-----+---------+----------------+
| Field      | Type    | Null | Key | Default | Extra          |
+------------+---------+------+-----+---------+----------------+
| id_despesa | int(11) | NO   | PRI | NULL    | auto_increment |
| id_recurso | int(11) | NO   | MUL | NULL    |                |
+------------+---------+------+-----+---------+----------------+
'''
def insert_expense(id_resource: int):
	db = get_db()
	cursor = db.cursor(dictionary=True)
	insert_query = ('INSERT INTO keepit.despesa (id_recurso)'
						+ 'VALUES (%s)')
	data_insert = (id_resource,)
	cursor.execute(data_insert,insert_query)
	db.commit()
	cursor.close()
	db.close()


''' 
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
		'constante': BOOL,
		'automatica': BOOL,
		'dia_mes': 0,
		'status': 0
	}
	'''


''' 
keepit.despesa_incomum clue

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
