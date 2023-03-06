# import functools
from distutils.log import error
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, abort)
from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_db, db_insert, db_fetch, db_fetch_dict
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
import json
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport.requests
import os
import pathlib
import requests
import random
import datetime
from dateutil.relativedelta import relativedelta
from flask_mobility.decorators import mobile_template
import time

os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
serial = URLSafeTimedSerializer('.k;4q>E;"cV}#SV$') #strong key

client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")
GOOGLE_CLIENT_ID ="235729726809-m7hq0ieje7efrmvs4p03gtv4mi61s9nl.apps.googleusercontent.com"
flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="https://social.chans/callback"
)


bp = Blueprint('auth', __name__)

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = db_fetch_dict('SELECT * FROM `cult` WHERE `id` = %s', (user_id,), one=True)


@bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out', 'info')
    return redirect(url_for('home'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            session['prev_page'] = request.url
            flash("You must be logged in to view this page", "error")
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view

@bp.route("/googleLogin")
def google_login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    print(authorization_url)
    return redirect(authorization_url)

@bp.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)
    # if not session["state"] == request.args["state"]:
    #     abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)
    # time.sleep(5)
    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    name = id_info['name']
    username = name.lower().replace(" ", "") + "#" + str(random.randint(1000,9999))
    email = id_info['email']
    password = id_info['sub']

    user = db_fetch('SELECT * FROM  `cult` WHERE `email` = %s', (email,), one=True)
    if user is not None:
        session.clear()
        session['user_id'] = user[0]
        flash("login success" , "success")
        id = request.cookies.get('request_id')
        if user[-1]==1:
            return redirect(url_for('form1'))
        return redirect(url_for('home'))
    else:
        # Add user
        date = datetime.datetime.now()
        db_insert('INSERT INTO cult (name, email) VALUES (%s, %s)', (name, email))
        flash("Successfully created account", "info")
        # Auto-login
        user = db_fetch('SELECT * FROM  `cult` WHERE `email` = %s', (email,), one=True)
        session.clear()
        session['user_id'] = user[0]
    flash('Your account has been created. Now you can login to the ResNote extension and start exploring!', 'info')
    return redirect(url_for('form1'))
