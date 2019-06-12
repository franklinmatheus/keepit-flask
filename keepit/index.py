from flask import Blueprint, render_template
from keepit.auth import only_unlogged_user

bp = Blueprint('index', __name__)

@bp.route('/')
@only_unlogged_user
def index():
	return render_template('public/index.html')
