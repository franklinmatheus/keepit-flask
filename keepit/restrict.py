from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from keepit.db import get_db
from keepit.auth import login_required

bp = Blueprint('restrict',__name__,url_prefix='/restrict')

@bp.route('/index', methods=('GET', 'POST'))
@login_required
def index():
    if g.user != None:
	    return render_template('restrict/index.html')
    
    return render_template('public/index.html')


@bp.route('/revenues', methods=('GET', 'POST'))
@login_required
def revenues():
    return render_template('restrict/revenues.html')

@bp.route('/expenses', methods=('GET', 'POST'))
@login_required
def expenses():
    return render_template('restrict/expenses.html')

@bp.route('/common', methods=('GET', 'POST'))
def expenses_common():
    return render_template('restrict/expenses/common.html')

@bp.route('/uncommon', methods=('GET', 'POST'))
def expenses_uncommon():
    return render_template('restrict/expenses/uncommon.html')

@bp.route('/estimated', methods=('GET', 'POST'))
def expenses_estimated():
    return render_template('restrict/expenses/estimated.html')

@bp.route('/programmed', methods=('GET', 'POST'))
def expenses_programmed():
    return render_template('restrict/expenses/programmed.html')