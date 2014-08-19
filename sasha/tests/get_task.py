import json

import requests


payload = {
    "wid": 2,
    "ntask": 3
}


r = requests.get("http://test02cern.vs.os.yandex.net:5000/get_task?wid=2&ntask=3")

print r.text
