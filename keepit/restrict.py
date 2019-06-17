from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from keepit.db import update_common_revenues, update_common_expenses
from keepit.db_analysis import get_balance, get_expenses_info, get_revenues_info
from keepit.auth import login_required
import datetime

bp = Blueprint('restrict',__name__,url_prefix='/restrict')

@bp.route('/', methods=('GET', 'POST'))
@login_required
def home():
    curr_date = datetime.datetime.now()
    balance = get_balance(session.get('user_id'))
    expenses_info = get_expenses_info(session.get('user_id'),curr_date.month,curr_date.year)
    revenues_info = get_revenues_info(session.get('user_id'),curr_date.month,curr_date.year)
    curr_month = curr_date.strftime('%B') + ' ' + str(curr_date.year)
    return render_template('restrict/index.html',balance=balance,expenses_info=expenses_info,revenues_info=revenues_info,curr_month=curr_month)

'''
Before requests
'''
@bp.before_app_request
def check_common_resources():
    update_common_revenues(session.get('user_id'),datetime.datetime.now().strftime("%Y-%m-%d"))
    update_common_expenses(session.get('user_id'),datetime.datetime.now().strftime("%Y-%m-%d"))