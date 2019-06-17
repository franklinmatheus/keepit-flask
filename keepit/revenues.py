from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from keepit.db import get_db
from keepit.db import  insert_revenue_common, select_revenue_common, update_common_revenues
from keepit.db import insert_revenue_uncommon, select_revenue_uncommon
from keepit.db import update_common_revenue_constant, update_common_revenue_inconstant
from keepit.db import remove_resource, cancel_resource

from keepit.db_analysis import get_total_revenues_by_day, get_total_revenues_by_month

from keepit.auth import login_required
import datetime
import json

bp = Blueprint('revenues',__name__,url_prefix='/restrict/revenues')

@bp.route('/', methods=('GET', 'POST'))
@login_required
def home():
    result = get_total_revenues_by_day(session.get('user_id'))
    calendar_info = {}    
    for i in range(0,len(result)):
        calendar_info[i] = {
            'data_pagamento': result[i]['data_pagamento'].strftime("%Y-%m-%d"), 
            'quantidade': result[i]['quantidade'], 
            'total': result[i]['total']
        }
    info_type = 'revenues'
    
    chart_info = get_total_revenues_by_month(session.get('user_id'),datetime.datetime.now().year)
    return render_template('restrict/revenues.html',calendar_info=json.dumps(calendar_info),
        info_type=info_type,chart_info=json.dumps(chart_info),
        current_year=datetime.datetime.now().year)

@bp.route('/common', methods=('GET', 'POST'))
@login_required
def common():
    if request.method == 'POST':
        name = request.form['name']
        value = 0
        month_day = request.form['month_day']
        status = 1
        annotation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            error = 'A common revenue can not be automatic and inconstant'

        if 'value' in request.form:
            value = int(request.form['value'])

        if value <= 0 and automatic == True:
            error = 'The value must be higher than R$ 0'

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
                'payment_date':payment_date,'annotation_date':annotation_date,
                'cancelation_date':None,'automatic':automatic,
                'constant':constant,'status':status}

            insert_revenue_common(session.get('user_id'),data)
        
        elif error is not None:
            flash(error)

    common_revenues = select_revenue_common(session.get('user_id'))
    return render_template('restrict/revenues/common.html',common_revenues=common_revenues)

@bp.route('/common/<int:id>/delete', methods=['POST'])
@login_required
def delete_common(id):
    if request.method == 'POST':
        remove_resource(id)
    return redirect(url_for('revenues.common'))

@bp.route('/common/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_common(id):
    if request.method == 'POST':
        cancel_resource(id,datetime.datetime.now().strftime("%Y-%m-%d"))
    return redirect(url_for('revenues.common'))

@bp.route('/common/<int:id>/update/constant', methods=['POST'])
@login_required
def update_common_constant(id):
    if request.method == 'POST':
        update_common_revenue_constant(id)
    return redirect(url_for('revenues.common'))

@bp.route('/common/<int:id>/update/inconstant', methods=['POST'])
@login_required
def update_common_inconstant(id):
    if request.method == 'POST':
        value = request.form['value']
        update_common_revenue_inconstant(id,value)
    return redirect(url_for('revenues.common'))


@bp.route('/uncommon', methods=('GET', 'POST'))
@login_required
def uncommon():
    if request.method == 'POST':
        name = request.form['name']
        value = request.form['value']
        payment_date = request.form['payment_date']
        emitter = request.form['emitter']
        reason = request.form['reason']
        annotation_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error = None

        if payment_date == '':
            error = 'You must provide a payment date'
        elif payment_date > datetime.datetime.now().strftime("%Y-%m-%d"):
            error = 'Payment date can not be in the future'

        if error is None:
            data = {'name':name,'value':value,'payment_date':payment_date,
                'emitter':emitter,'reason':reason,'annotation_date':annotation_date,
                'cancelation_date':None}
            insert_revenue_uncommon(session.get('user_id'),data)
        elif error is not None:
            flash(error)

    uncommon_revenues = select_revenue_uncommon(session.get('user_id'))
    return render_template('restrict/revenues/uncommon.html',uncommon_revenues=uncommon_revenues)

@bp.route('/uncommon/<int:id>/delete', methods=['POST'])
@login_required
def delete_uncommon(id):
    if request.method == 'POST':
        remove_resource(id)
    return redirect(url_for('revenues.uncommon'))

@bp.route('/uncommon/<int:id>/cancel', methods=['POST'])
@login_required
def cancel_uncommon(id):
    if request.method == 'POST':
        cancel_resource(id,datetime.datetime.now().strftime("%Y-%m-%d"))
    return redirect(url_for('revenues.uncommon'))

'''
Before requests
'''
@bp.before_app_request
def check_common_revenues():
    update_common_revenues(session.get('user_id'),datetime.datetime.now().strftime("%Y-%m-%d"))
