from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from keepit.db import get_db, insert_expense_common, select_expense_common, update_common_expenses, update_common_expense_constant, update_common_expense_inconstant, remove_resource, cancel_resource
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
        status = 1
        anotation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payment_date = None
        error = None

        automatic = 0
        if 'automatic' in request.form:
            automatic = 1
        constant = 0
        if 'constant' in request.form:
            constant = 1

        if month_day == '':
            error = 'Inform a month day'

        if constant == 0 and automatic == 1:
            error = 'A common expense can not be automatic and inconstant'
        
        if error is None:
            if automatic == 1:
                temp_date = datetime.datetime.now()
                temp_day = int(month_day)
                if temp_day < temp_date.day:
                    payment_date = datetime.datetime(temp_date.year, temp_date.month, temp_day)
                elif temp_day > temp_date.day:
                    if temp_date.month == 1:
                        payment_date = datetime.datetime(temp_date.year-1, 12, temp_day)
                    else:
                        payment_date = datetime.datetime(temp_date.year, temp_date.month-1, temp_day)
                else:
                    payment_date = datetime.datetime.now().strftime("%Y-%m-%d")
            else:
                status = 0
               
            data = {'name':name,'value':value,'month_day':month_day,
                'payment_date':payment_date,'anotation_date':anotation_date,
                'cancelation_date':None,'automatic':automatic,
                'constant':constant,'status':status}

            insert_expense_common(session.get('user_id'),data)
        
        elif error is not None:
            flash(error)

    common_expenses = select_expense_common(session.get('user_id'))
    return render_template('restrict/expenses/common.html',common_expenses=common_expenses)

@bp.route('/common/<int:id>/delete', methods=['POST'])
@login_required
def delete_common(id):
    if request.method == 'POST':
        remove_resource(id)
    return redirect(url_for('expenses.common'))

@bp.route('/common/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_common(id):
    if request.method == 'POST':
        cancel_resource(id,datetime.datetime.now().strftime("%Y-%m-%d"))
    return redirect(url_for('expenses.common'))

@bp.route('/common/<int:id>/update/constant', methods=['POST'])
@login_required
def update_common_constant(id):
    if request.method == 'POST':
        update_common_expense_constant(id)
    return redirect(url_for('expenses.common'))

@bp.route('/common/<int:id>/update/inconstant', methods=['POST'])
@login_required
def update_common_inconstant(id):
    if request.method == 'POST':
        value = request.form['value']
        update_common_expense_inconstant(id,value)
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


'''
Before requests
'''
@bp.before_app_request
def check_common_expenses():
    update_common_expenses(session.get('user_id'),'2019-06-29')
