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
            fname= request.form['fname']
            lname = request.form['lname']
            name = fname + " " + lname
            num = request.form['num']
            gender = request.form['gender']
            dob = str(request.form['dob'])
            insta = request.form['insta']
            city = "Mohali"
            
            img = request.form['imge']
            
            db_connection = get_db()
            db = db_connection.cursor()
            db.execute("UPDATE `chansprofile` SET `name`=%s, `num`=%s, `gender`=%s, `dob`=%s, `insta`=%s, `city`=%s, `img`=%s WHERE `id`=%s",(name, num, gender, dob, insta, city, img, user_id))
            db_connection.commit()
            return redirect(url_for('waitlist'))
        return render_template(template)
    
    # @app.route("/profile", methods=('GET', 'POST'))
    # @mobile_template('home/profile.html')
    # def profile(template):

    #     if not g.user:
    #         return redirect(url_for('auth.google_login'))
    #     if request.method=='POST':
    #         user_id = g.user['id']
    #         num = request.form['num']
    #         gender = request.form['gender']
    #         college = request.form['college']
    #         insta = str(request.form['insta'])
    #         img = request.form['imge']
            
    #         db_connection = get_db()
    #         db = db_connection.cursor()
    #         db.execute("UPDATE `cult` SET `num`=%s, `gender`=%s, `college`=%s, `insta`=%s, `img`=%s WHERE `id`=%s",(num, gender, college, insta, img, user_id))
    #         db_connection.commit()
    #         return redirect(url_for("profile"))
    #     return render_template(template)
    
    # @app.route("/join", methods=('GET', 'POST'))
    # @mobile_template('home/join.html')
    # def join(template):

    #     if not g.user:
    #         return redirect(url_for('auth.google_login'))
        
    #     if g.user['verification'] == 0:
    #         return redirect(url_for('verify'))
        
    #     if g.user['form']==1:
    #         return redirect(url_for('form1'))
        
    #     if request.method=='POST':
    #         user_id = g.user['id']
    #         img = request.form['img']
            
    #         db_connection = get_db()
    #         db = db_connection.cursor()
    #         db.execute("UPDATE `cult` SET `img`=%s WHERE `id`=%s",(img, user_id))
    #         db_connection.commit()
    #         return redirect(url_for('join'))

            
    #     users = db_fetch('SELECT * FROM  `cult` WHERE `tble`=%s', (g.user['tble'],))
    #     if g.user['tble']==0:
            
    #         # db_connection = get_db()
    #         # db = db_connection.cursor()
    #         # db.execute("SELECT MAX(tble) AS max FROM cult")
    #         # max = db.fetchall()
    #         # user = db_fetch('SELECT * FROM  `cult` WHERE `tble`=%s', (max[0][0],))
    #         # print(len(user))
    #         # if len(user)>4:
    #         #     tle = max[0][0] + 1
    #         #     numppl = 4 - 1
    #         # else:
    #         #     if max[0][0] == 0:
    #         #         tle = max[0][0] + 1
    #         #         numppl = 4- 1
    #         #     else:
    #         #         tle = max[0][0]
    #         #         numppl = 4 - len(user)
    #         # print(numppl, tle, "adca")
    #         db_connection = get_db()
    #         db = db_connection.cursor()
    #         # db.execute("UPDATE `cult` SET `tble`=%s WHERE `id`=%s",(tle , g.user['id']))
    #         db.execute("UPDATE `cult` SET `status`=%s WHERE `id`=%s",(1 , g.user['id']))
    #         db_connection.commit()
    #         return redirect(url_for('wait'))
    #     # print(users)
    #     return render_template(template, users=users, np=len(users))
        
    @app.route("/waitlist")
    @mobile_template('home/waitlist.html')
    def wait(template):
        # if not g.user:
        #     return redirect(url_for('auth.google_login'))
        return render_template(template)
    
    @app.route("/metthroughwhom")
    @mobile_template('home/challenge.html')
    def challenge(template):
        return render_template(template)
    
    @app.route("/result")
    @mobile_template('home/result.html')
    def result(template):
        if not g.user:
            return redirect(url_for('auth.google_login'))
        return render_template(template)
    # @app.route("/verify")
    # @mobile_template('home/verify.html')
    # def verify(template):
    #     if g.user:
    #         if not g.user['num']:
    #             return redirect(url_for('form1'))
    #     return render_template(template)
    
    
    # @app.route("/status", methods=('GET', 'POST'))
    # @mobile_template('home/status.html')
    # def status(template):
    #     if not g.user:
    #         return redirect(url_for('auth.google_login'))
        
    #     if request.method=='POST':
    #         user_id = g.user['id']
    #         img = request.form['img']
            
    #         db_connection = get_db()
    #         db = db_connection.cursor()
    #         db.execute("UPDATE `cult` SET `img`=%s WHERE `id`=%s",(img, user_id))
    #         db_connection.commit()
    #         return redirect(url_for('status'))

            
    #     users = db_fetch('SELECT * FROM  `cult` WHERE `tble`=%s', (g.user['tble'],))
    #     if g.user['tble']==0:
    #         db_connection = get_db()
    #         db = db_connection.cursor()
    #         db.execute("SELECT MAX(tble) AS max FROM cult")
    #         max = db.fetchall()
    #         user = db_fetch('SELECT * FROM  `cult` WHERE `tble`=%s', (max[0][0],))
    #         print(len(user))
    #         if len(user)>4:
    #             tle = max[0][0] + 1
    #             numppl = 4 - 1
    #         else:
    #             if max[0][0] == 0:
    #                 tle = max[0][0] + 1
    #                 numppl = 4- 1
    #             else:
    #                 tle = max[0][0]
    #                 numppl = 4 - len(user)
    #         print(numppl, tle, "adca")
    #         db_connection = get_db()
    #         db = db_connection.cursor()
    #         db.execute("UPDATE `cult` SET `tble`=%s WHERE `id`=%s",(tle , g.user['id']))
    #         db.execute("UPDATE `cult` SET `status`=%s WHERE `id`=%s",(1 , g.user['id']))
    #         db_connection.commit()
    #         return redirect(url_for('status'))
    #     # print(users)
    #     return render_template(template, users=users, np=len(users))
        
    
    # @app.route("/status/2", methods=('GET', 'POST'))
    # @mobile_template('home/status.html')
    # def arrived(template):
    #     if not g.user:
    #         return redirect(url_for('auth.google_login'))
        
    #     if g.user['status'] == 1:
    #         db_connection = get_db()
    #         db = db_connection.cursor()
    #         db.execute("UPDATE `cult` SET `status`=%s WHERE `id`=%s",(2 , g.user['id']))
    #         db_connection.commit()
    #         db.close()
            
    #         # print(users)
    #         return redirect(url_for('join'))
        
    #     return redirect(url_for('join'))
    
    # @app.route("/status/3", methods=('GET', 'POST'))
    # @mobile_template('home/status.html')
    # def cancel(template):
    #     if not g.user:
    #         return redirect(url_for('auth.google_login'))
        
    #     db_connection = get_db()
    #     db = db_connection.cursor()
    #     db.execute("UPDATE `cult` SET `status`=%s WHERE `id`=%s",(3 , g.user['id']))
    #     db_connection.commit()
    #     db.close()
        
    #     # print(users)
    #     return redirect(url_for('thanks2'))
            
    # @app.route("/status/1", methods=('GET', 'POST'))
    # @mobile_template('home/status.html')
    # def joinback(template):
    #     if not g.user:
    #         return redirect(url_for('auth.google_login'))
        
    #     db_connection = get_db()
    #     db = db_connection.cursor()
    #     db.execute("UPDATE `cult` SET `status`=%s WHERE `id`=%s",(1 , g.user['id']))
    #     db_connection.commit()
    #     db.close()
        
    #     # print(users)
    #     return redirect(url_for('join'))
            
    # @app.route("/hi")
    # @mobile_template('home/thanks.html')
    # def thanks(template):
    #     if g.user:
    #         return render_template(template)
    
    # @app.route("/thanks2")
    # @mobile_template('home/thanks2.html')
    # def thanks2(template):
    #     if g.user:
    #         if not g.user['num']:
    #             return redirect(url_for('form1'))
    #     return render_template(template)
    
    # @app.route("/feedback")
    # @mobile_template('home/feedback.html')
    # def feedback(template):
        if g.user:
            if not g.user['num']:
                return redirect(url_for('form1'))
        return render_template(template)
    
    
    # user authentication
    from . import auth
    app.register_blueprint(auth.bp)


    return app

app = create_app()
