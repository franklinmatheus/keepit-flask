from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from keepit.db_analysis import get_total_expenses_by_month, get_total_revenues_by_month
from keepit.auth import login_required

import datetime
import json

from statsmodels.tsa.holtwinters import ExponentialSmoothing
import pandas as pd


bp = Blueprint('analysis',__name__,url_prefix='/analysis')

@bp.route('/', methods=('GET', 'POST'))
@login_required
def home():
    chart_info_expenses = get_total_expenses_by_month(session.get('user_id'),datetime.datetime.now().year)
    chart_info_revenues = get_total_revenues_by_month(session.get('user_id'),datetime.datetime.now().year)
   
    df_expenses = pd.DataFrame(chart_info_expenses)
    df_revenues = pd.DataFrame(chart_info_revenues)
    df_joined = pd.merge(df_expenses, df_revenues, how='outer', on=['mes', 'mes'], suffixes=['_expenses', '_revenues'])
    df_joined = df_joined.fillna(0.0)

    data_expenses = []
    if len(df_joined['total_expenses'].values) == 1:
        data_expenses = [0,df_joined['total_expenses'].values]
    else:
        data_expenses = df_joined['total_expenses'].values

    model = ExponentialSmoothing(data_expenses)
    model_fit = model.fit()
    next_step_expenses = model_fit.predict(len(data_expenses), len(data_expenses))
    
    data_revenues = []
    if len(df_joined['total_revenues'].values) == 1:
        data_revenues = [0,df_joined['total_revenues'].values]
    else:
        data_revenues = df_joined['total_revenues'].values

    model = ExponentialSmoothing(data_revenues)
    model_fit = model.fit()
    next_step_revenues = model_fit.predict(len(data_revenues), len(data_revenues))

    next_step = next_step_revenues[0] - next_step_expenses[0]
    next_step = round(next_step,2)
    df_joined['diff'] = df_joined['total_revenues'] - df_joined['total_expenses']

    diff_values = df_joined[['diff','mes']].T.to_dict()

    return render_template('restrict/analysis.html',chart_info_expenses=json.dumps(chart_info_expenses),
        chart_info_revenues=json.dumps(chart_info_revenues),
        current_year=datetime.datetime.now().year,diff_values=json.dumps(diff_values),next_step=next_step,info_diff=df_joined['diff'].sum())