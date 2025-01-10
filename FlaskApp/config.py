import json

with open("/var/www/FlaskApp/FlaskApp/.client_secret.json") as config_file:
    config = json.load(config_file)
