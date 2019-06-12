import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash
from keepit.db import insert_user, check_login, select_user_by_id, select_user_by_credentials

bp = Blueprint('auth',__name__,url_prefix='/auth')

def only_unlogged_user(view):
	@functools.wraps(view)
	def wrapped_view(**kwargs):
		if g.user is not None:
			return redirect(url_for('restrict.home'))
		return view(**kwargs)
	return wrapped_view

@bp.route('/register', methods=('GET', 'POST'))
@only_unlogged_user
def register():
	if request.method == 'POST':
		fname = request.form['fname']
		lname = request.form['lname']
		born = request.form['born']
		username = request.form['username']
		confirm_password = request.form['cpassword']
		password = request.form['password']
		error = None

		if not username:
			error = 'Username is required'
		elif not password:
			error = 'Password is required'
		elif password != confirm_password:
			error = 'Password confirmation failed'
		else:
			user = check_login(username)
			if user is not None:
				error = 'Username already exists'

		if error is None:
			data = {'fname':fname,'lname':lname,'born':born,'username':username,'password':password}
			insert_user(data)
			return redirect(url_for('auth.login'))

		flash(error)

	return render_template('auth/register.html')

@bp.route('/login', methods=('GET', 'POST'))
@only_unlogged_user
def login():
	if request.method == 'POST':
		username = request.form['username']
		password = request.form['password']
		error = None

		user = select_user_by_credentials(username,password)
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
		user = select_user_by_id(user_id)
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