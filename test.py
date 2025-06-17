import json
import os

if os.path.exists("src/app.py"):
    import src.app as app
else:
     import app

with open("data.json", "r") as data: 
     data = data.read()

event = json.loads(data)

print(event)

retorno = app.handler(event, context=False)

print(retorno)

      