from flask import Blueprint, jsonify, request
from superset.dtable.mod_tables.serverside.serverside_table import ServerSideTable
import requests
import json
import re
import urllib.request
from bs4 import BeautifulSoup

class TableBuilder(object):

    def druid_data(self,request):

         print("Generate SQL")
         chart_id = self.request_values["chart_id"]
         s_query = self.request_values["sql_query"]
         curr_line = -1
         length = s_query.count('\n')
         druid_sql = ""
         where= " WHERE 1=1"
         for line in s_query.splitlines():
          curr_line += 1
          if line.startswith("WHERE "):
            where = " "
          if curr_line == length:
           if line.startswith("LIMIT "):
            print("LIMIT removed")
          elif curr_line == 0:
           druid_sql += line
          else:
           druid_sql += line
         druid_sql = druid_sql.replace('"','\\"')
         druid_sql += where
         self.request_values = request.values
         print("Druid SQL Column List Get")
         columns = self.create_column_config(request)

         print('select done')
         for i in range(len(columns)):
           search_col = 'sSearch_' + str(i)
           druid_col = columns[i]["data_name"]
           if self.request_values[search_col]:
             druid_sql += 'AND \\"' + columns[i]["data_name"] + '\\"' +  " = \'" +  self.request_values[search_col] + "\' "

         if self.request_values["query_limit"].isdigit():
             query_limit = self.request_values["query_limit"]
         else:
             query_limit = 10000

         druid_sql += " LIMIT " + str(query_limit)
         druid_sql = "{ \"query\" : " + "\"" + druid_sql + "\" }"
         druid_obj = json.loads(druid_sql)
         druid_request = "https://druid-query.internal.nets-analytics.net:8282/druid/v2/sql/"
         rp=requests.post(druid_request, json = druid_obj)
         return rp.json()

    def create_column_config(self, request):
        print("Create column list")
        self.request_values = request.values
        chart_id = self.request_values["chart_id"]
        s_query = self.request_values["sql_query"]
        column_list = "[ "
        order = 1
        last_line = 0
        length = len(s_query.splitlines())

        for line in s_query.splitlines():
         if line == "FROM":
          break
         last_line += 1

        for line in s_query.splitlines():
         if line == "FROM":
          break
         column = line.partition("\" AS ") [2]

         if order != last_line:
          column = column[:-1]

         column_list += "{ \"data_name\":" + column + " , \"column_name\": " + column +  " , \"default\": \"\", \"order\": "  + str(order) + " , \"searchable\": true } ,"
         order += 1
        columns = column_list[:-3] + " } ]"
        columns = json.loads(columns)

        return columns


    def collect_data_clientside(self):
        return {'data': DATA_SAMPLE}

    def collect_data_serverside(self, request):
        self.request_values = request.values
        return ServerSideTable(request, self.druid_data(request), self.create_column_config(request)).output_result()
