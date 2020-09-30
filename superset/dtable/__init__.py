from flask import Flask, redirect, session
from superset.dtable.mod_tables.models import TableBuilder


flask_app = Flask(__name__)

table_builder = TableBuilder()


from superset.dtable.common.routes import main
from superset.dtable.mod_tables.controllers import tables


# Register the different blueprints
flask_app.register_blueprint(main)
flask_app.register_blueprint(tables)
