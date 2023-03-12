import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import g
import mysql.connector as mysql



# server IP address/domain name
MYSQL_HOST = "sg2plzcpnl476821.prod.sin2.secureserver.net"
# database name
MYSQL_DATABASE = "resnote_db"
# user
MYSQL_USER = "resnote"
# password
MYSQL_PASSWORD = "venuS@900#"

###linkedin app configuration

client_id='86cnup9lqxcazk'
client_secret='oXGgQPvopDgJcmxs'
scope=["r_liteprofile", "r_emailaddress"]
redirect_url="/linkedin/auth"
redirect_to="/linkedin/auth"


# Add the mysql db_connection to g
# NOTE: create a cursor before executing any sql commands
def get_db():
    db = mysql.connect(
            host=MYSQL_HOST,
            database=MYSQL_DATABASE,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
        )
    return db


# close connection to db
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def db_insert(query, values=()):
    db_connection = get_db()
    db = db_connection.cursor()
    db.execute(query, values)
    db_connection.commit()
    db.close()

#returns tuple
def db_fetch(query, args=(), one=False):
    db_connection = get_db()
    db = db_connection.cursor()
    db.execute(query, args)
    rv=db.fetchall()
    db.close()

    return (rv[0] if rv else None) if one else rv


#returns dictionary {col:val}
def db_fetch_dict(query, args=(), one=False):
    db_connection = get_db()
    db = db_connection.cursor()
    db.execute(query, args)
    try:
        if one:
            rv = dict(zip(db.column_names, db.fetchone()))
        else:
            rv = dict(zip(db.column_names, db.fetchall()))
    except:
        rv = None
    db.close()
    return rv

def db_fetch_notebooks(query, args=(), one=False):
    db_connection = get_db();
    db = db_connection.cursor();
    db.execute(query, args)
    try:
        if one:
            rv = dict(zip(db.column_names, db.fetchone()))
        else:
            a = db.fetchall()
            rv = dict(zip(range(len(a)), a))
    except:
        rv = None
    db.close()
    return rv


def sendmail(name, email):
    # Send email for guide
            sender = "hello@chans.social"

            message = MIMEMultipart("alternative")
            message["Subject"] = "Join Chans Social event today"
            message["From"] = sender
            message["To"] = email
            text = """
            Hi {},<br><br>

            We are hosting a chans🤞social experience today over a dinner in H5 mess. Would you like to be considered for a spot?
            <br><br>
            Send us a Hi on WhatsApp by simply clicking on this <a href='https://wa.me/918249069736?text=Hi' target='_blank'>link</a> and you'll be considered for tonight's social experience with 3 new people.
            <br><br>
            Saswat Pattnaik <br>
            8249069736
            
            """.format(name)
            message.attach(MIMEText(text, "html"))
            server = smtplib.SMTP_SSL("smtp.zoho.in", 465)
            server.login(sender, "Sheldon$73")
            server.sendmail(sender, email, message.as_string())
            server.close()


sendmail('Saswat', 'saswatpattnaik98@gmail.com')
# users = db_fetch('SELECT * FROM  `cult`')
# for user in users:
#     print((user[1], user[2]))
#     sendmail(user[1], user[2])