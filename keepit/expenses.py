from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from keepit.db import get_db
from keepit.auth import login_required

bp = Blueprint('expenses',__name__,url_prefix='/restrict/expenses')

@bp.route('/', methods=('GET', 'POST'))
@login_required
def home():
    return render_template('restrict/expenses.html')

@bp.route('/common', methods=('GET', 'POST'))
@login_required
def common():
    return render_template('restrict/expenses/common.html')

@bp.route('/uncommon', methods=('GET', 'POST'))
@login_required
def uncommon():
    return render_template('restrict/expenses/uncommon.html')

@bp.route('/estimated', methods=('GET', 'POST'))
@login_required
def estimated():
    return render_template('restrict/expenses/estimated.html')

@bp.route('/programmed', methods=('GET', 'POST'))
@login_required
def programmed():
    return render_template('restrict/expenses/programmed.html')