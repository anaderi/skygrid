import json
import requests



r = requests.get("http://test02cern.vs.os.yandex.net:5000/get_jobs?wid=1&njob=1")

print r.text
