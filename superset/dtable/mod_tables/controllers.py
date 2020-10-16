from flask import Blueprint, jsonify, request, redirect, url_for
from superset.dtable import table_builder
from flask_appbuilder.security.decorators import has_access
import requests
import json
import re
import urllib.request
from bs4 import BeautifulSoup
from superset.extensions import appbuilder
from flask_oidc import OpenIDConnect
from flask_login import current_user

tables = Blueprint('tables', __name__, url_prefix='/tables')


@tables.route("/serverside_table", methods=['GET'])
def serverside_table_content():
        sm = appbuilder.sm
        oidc = sm.oid

#        @appbuilder.sm.oid.require_login
        def handle_login():
#          if oidc.user_loggedin:
          if current_user.is_authenticated:
           data = table_builder.collect_data_serverside(request)
           return jsonify(data)
          else:
           return redirect('https://superset.nets-analytics.net/login')
        return handle_login()


@tables.route("/get_columns", methods=['GET'])
def get_sql_columns():
        sm = appbuilder.sm
        oidc = sm.oid

#        @appbuilder.sm.oid.require_login
        def handle_login_2():
#          if oidc.user_loggedin:
          if current_user.is_authenticated:
            print("User logged in")
            s_query = request.args.get('sql_query')
            chart_id = request.args.get('chart_id')
            column_list = "[ "
            column_list_return= ""
            for line in s_query.splitlines():
               if line == "FROM":
                 break
               column = line.partition("\" AS ") [2]
               column = column[:-1]
               column_list += "{ \"data\" : " + column + "} ,"
            column_list_return = column_list[:-3] + "\" } ]"
          else:
            print("No user logged in")
            column_list_return = redirect('https://superset.nets-analytics.net/login')
          return column_list_return

        return handle_login_2()
