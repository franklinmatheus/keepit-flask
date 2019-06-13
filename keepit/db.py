import mysql.connector
import datetime
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
+------------+-------------+------+-----+---------+----------------+

keepit.credenciais_usuario clue
+------------+--------------+------+-----+---------+-------+
| Field      | Type         | Null | Key | Default | Extra |
+------------+--------------+------+-----+---------+-------+
| id_usuario | int(11)      | NO   | PRI | NULL    |       |
| login      | varchar(45)  | NO   |     | NULL    |       |
| senha      | varchar(150) | NO   |     | NULL    |       |
+------------+--------------+------+-----+---------+-------+
'''
def insert_user(data: dict):
	db = get_db()
	cursor = db.cursor(dictionary=True)

	insert_user = ('INSERT INTO keepit.usuario (fnome, lnome, nascimento) VALUES (%s, %s, %s)')
	data_user = (data['fname'], data['lname'], data['born'])
	cursor.execute(insert_user,data_user)
	id_user = cursor.lastrowid

	insert_credentials = ('INSERT INTO keepit.credenciais_usuario (id_usuario,login,senha) VALUES (%s, %s, %s)')
	data_credentials = (id_user,data['username'],data['password'])
	cursor.execute(insert_credentials,data_credentials)

	db.commit()
	cursor.close()
	db.close()

def check_login(login: str):
	db = get_db()
	cursor = db.cursor(dictionary=True)

	select_user = ('SELECT * FROM keepit.credenciais_usuario WHERE keepit.credenciais_usuario.login = %s')
	data_user = (login,)
	cursor.execute(select_user,data_user)
	user = cursor.fetchone()
	cursor.close()
	db.close()

	return user

def select_user_by_id(id: int):
	db = get_db()
	cursor = db.cursor(dictionary=True)
	
	select_user = ('SELECT * FROM (keepit.usuario JOIN keepit.credenciais_usuario '
						+ 'ON keepit.usuario.id_usuario=keepit.credenciais_usuario.id_usuario) '
						+ 'WHERE keepit.usuario.id_usuario = %s')
	data_user = (id,)
	cursor.execute(select_user,data_user)
	user = cursor.fetchone()
	cursor.close()
	db.close()

	return user

def select_user_by_credentials(username: str, password: str):
	db = get_db()
	cursor = db.cursor(dictionary=True)

	select_user = ('SELECT * FROM (keepit.usuario JOIN keepit.credenciais_usuario '
						+ 'ON keepit.usuario.id_usuario=keepit.credenciais_usuario.id_usuario) '
						+ 'WHERE keepit.credenciais_usuario.login = %s AND keepit.credenciais_usuario.senha = %s')
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
| nome              | varchar(45) | NO   |     | NULL    |                |
| data_cancelamento | date        | YES  |     | NULL    |                |
| data_anotacao     | datetime    | NO   |     | NULL    |                |
+-------------------+-------------+------+-----+---------+----------------+

keepit.pagamento_recurso clue
+----------------+---------+------+-----+---------+-------+
| Field          | Type    | Null | Key | Default | Extra |
+----------------+---------+------+-----+---------+-------+
| id_recurso     | int(11) | NO   | PRI | NULL    |       |
| data_pagamento | date    | NO   |     | NULL    |       |
| valor          | float   | NO   |     | NULL    |       |
+----------------+---------+------+-----+---------+-------+

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

	insert_query = ('INSERT INTO keepit.recurso (id_usuario, nome, data_cancelamento, data_anotacao)'
						+ 'VALUES (%s, %s, %s, %s)')
	data_insert = (id_user,data['name'],data['cancelation_date'],data['anotation_date'])
	cursor.execute(insert_query,data_insert)
	id_resource = cursor.lastrowid

	insert_query = ('INSERT INTO keepit.pagamento_recurso (id_recurso, data_pagamento, valor)'
						+ 'VALUES (%s, %s, %s)')
	data_insert = (id_resource,data['payment_date'],data['value'])
	cursor.execute(insert_query,data_insert)

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
		+ '(((keepit.recurso JOIN keepit.despesa ON keepit.recurso.id_recurso=keepit.despesa.id_recurso) '
		+ 'JOIN keepit.despesa_comum ON keepit.despesa.id_despesa=keepit.despesa_comum.id_despesa) '
        + 'JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_pagamento = '
		+ '(SELECT keepit.pagamento_recurso.id_pagamento FROM keepit.pagamento_recurso '
		+ 'WHERE keepit.pagamento_recurso.id_recurso=keepit.recurso.id_recurso '
        + 'ORDER BY keepit.pagamento_recurso.data_pagamento DESC '
        + 'LIMIT 1)) '
		+ 'WHERE keepit.recurso.id_usuario=%s ORDER BY keepit.recurso.data_anotacao DESC')

	select_data = (id_user,)
	cursor.execute(select_query,select_data)
	results = cursor.fetchall()
	cursor.close()
	db.close()

	return results

def update_common_expenses(id_user: int, today):
	db = get_db()
	cursor = db.cursor(dictionary=True)

	select_query = ('(SELECT keepit.despesa_comum.id_despesa,keepit.despesa_comum.automatica, '
		+ 'keepit.recurso.id_recurso,keepit.pagamento_recurso.valor,keepit.pagamento_recurso.data_pagamento FROM '
		+'(((keepit.recurso JOIN keepit.despesa ON keepit.recurso.id_recurso=keepit.despesa.id_recurso) '
		+ 'JOIN keepit.despesa_comum ON keepit.despesa.id_despesa=keepit.despesa_comum.id_despesa) '
		+ 'JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_pagamento = '
		+ '(SELECT keepit.pagamento_recurso.id_pagamento FROM keepit.pagamento_recurso '
		+ 'WHERE keepit.pagamento_recurso.id_recurso=keepit.recurso.id_recurso '
		+ 'ORDER BY keepit.pagamento_recurso.data_pagamento DESC LIMIT 1))'
		+ 'WHERE TIMESTAMPDIFF(MONTH,keepit.pagamento_recurso.data_pagamento,%s) > 0 '
		+ 'AND keepit.recurso.id_usuario=%s '
		+ ')UNION'
		+ '(SELECT keepit.despesa_comum.id_despesa,keepit.despesa_comum.automatica, '
		+ 'keepit.recurso.id_recurso,keepit.pagamento_recurso.valor,keepit.pagamento_recurso.data_pagamento FROM '
		+ '(((keepit.recurso JOIN keepit.despesa ON keepit.recurso.id_recurso=keepit.despesa.id_recurso) '
		+ 'JOIN keepit.despesa_comum ON keepit.despesa.id_despesa=keepit.despesa_comum.id_despesa) '
		+ 'JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_pagamento = '
		+ '(SELECT keepit.pagamento_recurso.id_pagamento FROM keepit.pagamento_recurso '
		+ 'WHERE keepit.pagamento_recurso.id_recurso=keepit.recurso.id_recurso '
		+ 'ORDER BY keepit.pagamento_recurso.data_pagamento DESC LIMIT 1)) '
		+ 'WHERE keepit.pagamento_recurso.data_pagamento IS NULL AND keepit.recurso.id_usuario=%s)')
	select_data = (today,id_user,id_user)
	cursor.execute(select_query,select_data)
	results = cursor.fetchall()
	
	automatic = []
	nonautomatic = []

	for result in results:
		if result['automatica'] == 1:
			automatic.append(result)
		else:
			nonautomatic.append(result)

	for curr in nonautomatic:
		update_query = ('UPDATE keepit.despesa_comum SET keepit.despesa_comum.status = 0 WHERE keepit.despesa_comum.id_despesa = %s')
		update_data = (curr['id_despesa'],)
		cursor.execute(update_query,update_data)

	for curr in automatic:
		payment_date = None
		last_update = curr['data_pagamento']
		
		if last_update.month == 12:
			payment_date = datetime.datetime(last_update.year+1, 1, last_update.day)
		else:
			payment_date = datetime.datetime(last_update.year, last_update.month+1, last_update.day)

		insert_query = ('INSERT INTO keepit.pagamento_recurso (id_recurso,data_pagamento,valor) values (%s, %s, %s)')
		inser_data = (curr['id_recurso'],payment_date,curr['valor'])
		cursor.execute(insert_query,inser_data)
	
	db.commit()
	cursor.close()
	db.close()


def update_common_expense_constant(id_resource: int):
	db = get_db()
	cursor = db.cursor(dictionary=True)

	select_query = ('SELECT keepit.pagamento_recurso.valor FROM '
	+ '(((keepit.recurso JOIN keepit.despesa ON keepit.recurso.id_recurso=keepit.despesa.id_recurso) '
    + 'JOIN keepit.despesa_comum ON keepit.despesa.id_despesa=keepit.despesa_comum.id_despesa) '
    + 'JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_pagamento = '
	+ '(SELECT keepit.pagamento_recurso.id_pagamento FROM keepit.pagamento_recurso '
	+ 'WHERE keepit.pagamento_recurso.id_recurso=keepit.recurso.id_recurso '
    + 'ORDER BY keepit.pagamento_recurso.data_pagamento DESC LIMIT 1)) '
	+ 'WHERE keepit.recurso.id_recurso=%s')
	select_data = (id_resource,)
	cursor.execute(select_query,select_data)
	resource = cursor.fetchone()
	update_common_expense_inconstant(id_resource,resource['valor'])


def update_common_expense_inconstant(id_resource: int, value: float):
	db = get_db()
	cursor = db.cursor(dictionary=True)

	select_query = ('SELECT keepit.despesa_comum.dia_mes,keepit.despesa_comum.id_despesa,keepit.pagamento_recurso.data_pagamento FROM '
	+ '(((keepit.recurso JOIN keepit.despesa ON keepit.recurso.id_recurso=keepit.despesa.id_recurso) '
    + 'JOIN keepit.despesa_comum ON keepit.despesa.id_despesa=keepit.despesa_comum.id_despesa) '
    + 'JOIN keepit.pagamento_recurso ON keepit.pagamento_recurso.id_pagamento = '
	+ '(SELECT keepit.pagamento_recurso.id_pagamento FROM keepit.pagamento_recurso '
	+ 'WHERE keepit.pagamento_recurso.id_recurso=keepit.recurso.id_recurso '
    + 'ORDER BY keepit.pagamento_recurso.data_pagamento DESC LIMIT 1)) '
	+ 'WHERE keepit.recurso.id_recurso=%s')
	select_data = (id_resource,)
	cursor.execute(select_query,select_data)
	resource = cursor.fetchone()

	payment_date = None
	if resource['data_pagamento'] is not None:
		if resource['data_pagamento'].month == 12:
			payment_date = datetime.datetime(resource['data_pagamento'].year+1, 1, resource['data_pagamento'].day)
		else:
			payment_date = datetime.datetime(resource['data_pagamento'].year, resource['data_pagamento'].month+1, resource['data_pagamento'].day)
	else:
		temp_date = datetime.datetime.now()
		temp_day = resource['dia_mes']
		if temp_day < temp_date.day:
			payment_date = datetime.datetime(temp_date.year, temp_date.month, temp_day)
		elif temp_day > temp_date.day:
			if temp_date.month == 1:
				payment_date = datetime.datetime(temp_date.year-1, 12, temp_day)
			else:
				payment_date = datetime.datetime(temp_date.year, temp_date.month-1, temp_day)
		else:
			payment_date = datetime.datetime.now().strftime("%Y-%m-%d")

	insert_query = ('INSERT INTO keepit.pagamento_recurso (id_recurso,data_pagamento,valor) values (%s, %s, %s)')
	inser_data = (id_resource,payment_date,value)
	cursor.execute(insert_query,inser_data)
	
	update_query = ('UPDATE keepit.despesa_comum SET keepit.despesa_comum.status = 1 WHERE keepit.despesa_comum.id_despesa = %s')
	update_data = (resource['id_despesa'],)
	cursor.execute(update_query,update_data)
	
	db.commit()
	cursor.close()
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
| data_anotacao     | date        | NO   |     | NULL    |                |
+-------------------+-------------+------+-----+---------+----------------+

keepit.despesa clue
+------------+---------+------+-----+---------+----------------+
| Field      | Type    | Null | Key | Default | Extra          |
+------------+---------+------+-----+---------+----------------+
| id_despesa | int(11) | NO   | PRI | NULL    | auto_increment |
| id_recurso | int(11) | NO   | MUL | NULL    |                |
+------------+---------+------+-----+---------+----------------+

keepit.despesa_incomum clue
+------------+-------------+------+-----+---------+-------+
| Field      | Type        | Null | Key | Default | Extra |
+------------+-------------+------+-----+---------+-------+
| id_despesa | int(11)     | NO   | PRI | NULL    |       |
| destino    | varchar(45) | NO   |     | NULL    |       |
+------------+-------------+------+-----+---------+-------+
'''
def insert_expense_uncommon(id_user: int, data: dict):
	'''
	The dictionary has to be as shown below:
	{
		'value': 0,
		'payment_date': 'dd/mm/yyyy',
		'name': 'abc',
		'cancelation_date': 'dd/mm/yyyy',
		'anotation_date': 'dd/mm/yyyy',
		'destino': 'abc'
	}
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

def cancel_resource(id_resource: int, cancelation_date):
	db = get_db()
	cursor = db.cursor(dictionary=True)
	update_query = ('UPDATE keepit.recurso SET keepit.recurso.data_cancelamento=%s'
		+ ' WHERE keepit.recurso.id_recurso=%s')
	update_data = (cancelation_date,id_resource)
	cursor.execute(update_query,update_data)
	db.commit()
	cursor.close()
	db.close()
