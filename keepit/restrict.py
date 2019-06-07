from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from keepit.db import get_db
from keepit.auth import login_required

bp = Blueprint('restrict',__name__,url_prefix='/restrict')

@bp.route('/', methods=('GET', 'POST'))
@login_required
def home():
	return render_template('restrict/index.html')