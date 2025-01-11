import json
import os
import pathlib
import requests

from flask import Flask, session, redirect, request, abort, render_template
from flask_mongoengine import MongoEngine
from . import mongoDB
from . import pb
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
from dotenv import load_dotenv
import google.auth.transport.requests

load_dotenv()

app = Flask(__name__)
database_URI = os.getenv("DATABASE_URI")
app.config["MONGODB_SETTINGS"] = {"host": database_URI}
app.secret_key = app.config.get("APP_SECRET_KEY")

db = MongoEngine()
db.init_app(app)


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = app.config.get("GOOGLE_CLIENT_ID")

client_secrets_file = os.path.join(pathlib.Path(__file__).parent, ".client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ],
    redirect_uri="https://weatherlookout.online/callback",
    # change the uri to be the domain
)

alive = 0
data = {}


def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorisation required
        else:
            return function()

    return wrapper


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/main")
@login_is_required
def protected_area():
    return render_template("main.html")


@app.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/tracker")
def tracker():
    current_weather_status = mongoDB.get_current_weather_record()
    return render_template(
        "tracker.html", current_weather_status=current_weather_status
    )


# where we deal with the response from google
@app.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # states don't match

    credentials = flow.credentials
    request_session = requests.session()
    cached_control = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_control)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token, request=token_request, audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    print(session["google_id"])

    session["name"] = id_info.get("name")
    print(session["name"])
    return redirect("/main")


@app.route("/keep_alive")
def keep_alive():
    global alive, data
    alive += 1
    keep_alive_count = str(alive)
    data["keep_alive"] = keep_alive_count
    parsed_json = json.dumps(data)
    print(parsed_json)
    return str(parsed_json)


@app.route("/get_temp_and_humidity", methods=["POST"])
def get_weather_details():
    temperature = request.form.get("temperature")
    humidity = request.form.get("humidity")
    print("Temperature:", temperature)
    print("Humidity:", humidity)

    if temperature and humidity:
        mongoDB.add_new_weather_data(
            temperature=float(temperature), humidity=float(humidity)
        )
        current_weather_status = mongoDB.get_current_weather_record()
        return render_template(
            "tracker.html", current_weather_status=current_weather_status
        )
    else:
        return "No data recieved"


if __name__ == "__main__":
    app.run(debug=True)
