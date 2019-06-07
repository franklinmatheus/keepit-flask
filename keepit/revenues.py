from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from keepit.db import get_db
from keepit.auth import login_required

bp = Blueprint('revenues',__name__,url_prefix='/restrict/revenues')

@bp.route('/', methods=('GET', 'POST'))
@login_required
def home():
    return render_template('restrict/revenues.html')

@bp.route('/common', methods=('GET', 'POST'))
@login_required
def common():
    return render_template('restrict/revenues/common.html')

@bp.route('/uncommon', methods=('GET', 'POST'))
@login_required
def uncommon():
    return render_template('restrict/revenues/uncommon.html')