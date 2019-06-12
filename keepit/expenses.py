from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from keepit.db import get_db, insert_expense_common, select_expense_common, remove_resource
from keepit.auth import login_required
import datetime

bp = Blueprint('expenses',__name__,url_prefix='/restrict/expenses')

@bp.route('/', methods=('GET', 'POST'))
@login_required
def home():
    return render_template('restrict/expenses.html')

@bp.route('/common', methods=('GET', 'POST'))
@login_required
def common():
    if request.method == 'POST':
        name = request.form['name']
        value = request.form['value']
        month_day = request.form['month_day']
        payment_date = request.form['payment_date']
        cancelation_date = request.form['cancelation_date']
        status = 1
        anotation_date = datetime.datetime.now().strftime("%Y-%m-%d")
        error = None

        automatic = 0
        if 'automatic' in request.form:
            automatic = 1
        constant = 0
        if 'constant' in request.form:
            constant = 1

        if month_day == '':
            error = 'Inform a month day'
        elif payment_date == '':
            error = 'Inform a payment date'
        elif cancelation_date == '':
            error = 'Inform a cancelation date'
        
        data = {'name':name,'value':value,'month_day':month_day,
            'payment_date':payment_date,'anotation_date':anotation_date,
            'cancelation_date':cancelation_date,'automatic':automatic,
            'constant':constant,'status':status}

        insert_expense_common(session.get('user_id'),data)
        
        if error is not None:
            flash(error)

    common_expenses = select_expense_common(session.get('user_id'))
    return render_template('restrict/expenses/common.html',common_expenses=common_expenses)

@bp.route('/common/<int:id>', methods=['POST'])
@login_required
def delete_common(id):
    if request.method == 'POST':
        remove_resource(id)
    return redirect(url_for('expenses.common'))

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