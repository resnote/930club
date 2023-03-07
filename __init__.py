import os
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
from flask import Flask, render_template, make_response, send_from_directory, g
from flask_mobility import Mobility
from flask_mobility.decorators import mobile_template
from distutils.log import error
from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for, abort)
from werkzeug.security import check_password_hash, generate_password_hash
from .db import get_db, db_insert, db_fetch, db_fetch_dict
import os

from dateutil.relativedelta import relativedelta
from flask_mobility.decorators import mobile_template
import pandas as pd


def create_app(test_config=None):
    # create and configure app
    app = Flask(__name__, instance_relative_config=True)
    app.config["MAX_CONTENT_LENGTH"] = 120 * 1024 * 1024
    app.config.from_mapping(SECRET_KEY='dev', DATABASE=os.path.join(app.instance_path, 'website.sqlite'))
    Mobility(app)

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # host sitemap
    @app.route('/sitemap', methods=["GET"])
    def sitemap():
        template = render_template('sitemap.xml')
        response = make_response(template)
        response.headers['ContentType'] = 'application/xml'
        return response

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.route("/")
    @mobile_template('home/home.html')
    def home(template):
        if g.user:
            if not g.user['num']:
                return redirect(url_for('form1'))
        return render_template(template)
    
    
    @app.route("/form1", methods=('GET', 'POST'))
    @mobile_template('home/form.html')
    def form1(template):

        if not g.user:
            return redirect(url_for('auth.google_login'))
        if request.method=='POST':
            user_id = g.user['id']
            num = request.form['num']
            gender = request.form['gender']
            college = request.form['college']
            insta = request.form['insta']
            
            db_connection = get_db()
            db = db_connection.cursor()
            db.execute("UPDATE `cult` SET `num`=%s, `gender`=%s, `college`=%s, `insta`=%s WHERE `id`=%s",(num, gender, college, insta, user_id))
            db_connection.commit()
            return redirect(url_for('thanks'))
        return render_template(template)
    
    @app.route("/join", methods=('GET', 'POST'))
    @mobile_template('home/join.html')
    def join(template):

        if not g.user:
            return redirect(url_for('auth.google_login'))
        
        if not g.user['tble']=='0':    
            db_connection = get_db()
            db = db_connection.cursor()
            db.execute("SELECT MAX(tble) AS max FROM cult")
            max = db.fetchall()
            user = db_fetch('SELECT * FROM  `cult` WHERE `tble` = %s', (max[0][0],))
            print(len(user))
            if len(user)>4:
                tle = max[0][0] + 1
                numppl = 1
            elif max[0][0] == 0:
                tle = max[0][0] + 1
                numppl = 1
            else:
                tle = max[0][0]
                numppl = len(user)
            print(numppl, tle, "adca")
            db_connection = get_db()
            db = db_connection.cursor()
            db.execute("UPDATE `cult` SET `tble`=%s WHERE `id`=%s",(tle , g.user['id']))
            db_connection.commit()
            return render_template(template, tle=tle, numppl=numppl)
        else:
            tle = g.user['tble']
            numppl = len(db_fetch('SELECT * FROM  `cult` WHERE `tble` = %s', (int(tle),)))
            return render_template(template, tle=tle, numppl=numppl)
        
        return render_template(template)
      
    @app.route("/thanks")
    @mobile_template('home/thanks.html')
    def thanks(template):
        if g.user:
            if not g.user['num']:
                return redirect(url_for('form1'))
        return render_template(template)
    
    # user authentication
    from . import auth
    app.register_blueprint(auth.bp)


    return app

app = create_app()
