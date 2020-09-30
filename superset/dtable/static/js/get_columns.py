import requests
import json
import re
import urllib.request

resp=requests.get('http://localhost:8088/superset/explore_json/?form_data=%7B"slice_id"%3A19%7D')
resp_dta=resp.json()
array= resp_dta['query']
print(str.array))

return array
