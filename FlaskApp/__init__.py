import json
import os
import pathlib
import requests

from flask import Flask, session, redirect, request, abort, render_template

from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests

app = Flask(__name__)
app.secret_key = "weathersecret"

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = (
    "489456852449-balvkioklqhrjc61peed6vh680ej4aj7.apps.googleusercontent.com"
)

client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=[
        "https://www.googleapis.com/auth/userinfo.profile",
        "https://www.googleapis.com/auth/userinfo.email",
        "openid",
    ],
    redirect_uri="http://127.0.0.1:5000/callback",
)

# change the redirect uri to being domain name


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


if __name__ == "__main__":
    app.run(debug=True)
