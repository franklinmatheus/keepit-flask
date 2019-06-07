import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from keepit.db import get_db

bp = Blueprint('auth',__name__,url_prefix='/auth')

@bp.route('/register', methods=('GET', 'POST'))
def register():
	if request.method == 'POST':
		fname = request.form['fname']
		lname = request.form['lname']
		born = request.form['born']
		username = request.form['username']
		confirm_password = request.form['cpassword']
		password = request.form['password']

		db = get_db()
		cursor = db.cursor(dictionary=True)
		error = None

		if not username:
			error = 'Username is required'
		elif not password:
			error = 'Password is required'
		elif password != confirm_password:
			error = 'Password confirmation failed'
		else:
			select_user = ('SELECT * FROM keepit.usuario WHERE login = %s')
			data_user = (username,)
			cursor.execute(select_user,data_user)
			user = cursor.fetchone()

			if user is not None:
				error = 'Username already exists'

		if error is None:
			insert_user = ('INSERT INTO keepit.usuario (fnome, lnome, nascimento, login, senha) VALUES (%s, %s, %s, %s, %s)')
			data_user = (fname, lname, born, username, password)
			cursor.execute(insert_user,data_user)
			db.commit()
			cursor.close()
			db.close()
			
			return redirect(url_for('auth.login'))

		flash(error)

	return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		db = get_db()
		cursor = db.cursor(dictionary=True)
		error = None

		select_user = ('SELECT * FROM keepit.usuario WHERE login = %s AND senha = %s')
		data_user = (username,password)
		cursor.execute(select_user,data_user)
		user = cursor.fetchone()
		if user is None:
			error = 'Username or password incorrects'

		if error is None:
			session.clear()
			session['user_id'] = user['id_usuario']
			return redirect(url_for('restrict.home'))

		flash(error)

	return render_template('auth/login.html')

@bp.before_app_request
def load_logged_in_user():
	user_id = session.get('user_id')
	
	if user_id is None:
		g.user = None
	else:
		db = get_db()
		cursor = db.cursor(dictionary=True)
		
		select_user = ('SELECT * FROM keepit.usuario WHERE id_usuario = %s')
		data_user = (user_id,)
		cursor.execute(select_user,data_user)
		user = cursor.fetchone()

		g.user = user

@bp.route('/logout')
def logout():
	session.clear()
	return redirect(url_for('index'))

def login_required(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is None:
			return redirect(url_for('auth.login'))
		return view(**kwargs)
	return wrapped_view
