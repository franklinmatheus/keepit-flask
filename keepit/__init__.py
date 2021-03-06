import os
from flask import Flask

def create_app(test_config=None):
	app = Flask(__name__,instance_relative_config=False)
	app.config.from_mapping(SECRET_KEY='dev')

	if test_config is None:
		app.config.from_pyfile('config.py',silent=True)
	else:
		app.config.from_mapping(test_config)
	
	try:
		os.makedirs(app.instance_path)
	except OSError:
		pass

	from . import auth
	app.register_blueprint(auth.bp)

	from . import index
	app.register_blueprint(index.bp)

	from . import restrict
	app.register_blueprint(restrict.bp)

	from . import analysis
	app.register_blueprint(analysis.bp)

	from . import expenses
	app.register_blueprint(expenses.bp)

	from . import revenues
	app.register_blueprint(revenues.bp)

	app.add_url_rule('/',endpoint='index')
	
	return app
