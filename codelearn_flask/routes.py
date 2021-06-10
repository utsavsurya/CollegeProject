from codelearn_flask import app,conn #,db 
from flask import render_template,url_for,redirect,flash,request,make_response
from codelearn_flask.forms import RegistrationForm,LoginForm
from codelearn_flask.models import Datas
from codelearn_flask.functions import log_to_db,temp_last_value,hum_last_value
import json
from time import time
from random import random         # remove later
import psycopg2
import psycopg2.extras
import datetime
import pytz




DB_HOST = "192.168.1.7"
DB_NAME = "iot_db"
DB_USER = "project"
DB_PASS = "123456"

@app.route("/")
@app.route('/Home')         #decorator function always has to have a function in it lalala
def homepage():
    return render_template("homepage.html",title="Home page")

@app.route('/Dashboard',methods=['GET'])
def dashboard():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    cur.execute("SELECT time,temperature,humidity FROM datas where time > now() - interval '1 minute';")
    t = cur.fetchall()
    cur.close()

    # time = [row[:] for row in t]
    time = [int(row[0].strftime("%H")) for row in t]
    Temperature = [row[1] for row in t]
    Humidity = [row[2] for row in t]
    data = [time ,Temperature, Humidity]

    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return render_template('Dashboard.html',title='Dashboard', label = response)
  

@app.route('/DataBoard',methods=['POST','GET']) # done  WHERE DATA FROM ARDUNIO IS COMMING VIA POST METHOD AND NEED TO BE HANDLED AND PUT INTO DATA BASE
def upload():
    if request.method == "POST":
        #log_to_db(request.get_json())
        request_data = request.get_json()
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cur = conn.cursor()
        cur.execute("INSERT INTO datas VALUES (%s, %s, %s, %s, %s, %s);",
                        (  
                            datetime.datetime.now(pytz.timezone('Asia/Kolkata')),
                            request_data['temp'],
                            request_data['water'],
                            request_data['ppl'],
                            request_data['pow'],
                            request_data['hum'],
                        ),
                    )
        conn.commit()
        cur.close()
    if request.method == "GET":
        return "hello"
    return render_template('DataBoard.html',title='DataBoard')

@app.route('/data', methods=["GET", "POST"])   # SENDING LIVE DATA TO GRAPHS
def data():

    # Data Format
    # [TIME, Temperature, Humidity]

    #Temperature = temp_last_value()
    #Humidity = hum_last_value()
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    cur.execute('SELECT temperature FROM datas ORDER BY "time" DESC LIMIT 1')
    t = cur.fetchall()
    cur.execute('SELECT humidity FROM datas ORDER BY "time" DESC LIMIT 1')
    h = cur.fetchall()
    cur.close()

    Temperature = t[0]
    Humidity = h[0]

    data = [time() * 1000, Temperature[0] , Humidity[0]]
    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response

@app.route('/test', methods=["GET", "POST"])
def test():

    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    cur.execute("SELECT time,temperature,humidity FROM datas where time > now() - interval '1 minute';")
    t = cur.fetchall()
    cur.close()

    # time = [row[:] for row in t]
    time = [int(row[0].strftime("%H")) for row in t]
    Temperature = [row[1] for row in t]
    Humidity = [row[2] for row in t]
    data = [time ,Temperature, Humidity]

    response = make_response(json.dumps(data))
    response.content_type = 'application/json'
    return response
    # return {"res":data}

@app.route('/Lookin',methods=['POST','GET'])   # done    LOGIN PAGE NOTHING TO DO HERE
def lookin():
    form = LoginForm()
    if form.validate_on_submit():
        if ((form.email.data =='utsav.jan@gmail.com' or form.email.data =='varshinidiwakar3@gmail.com' ) and form.password.data =='123456'):
            flash(f'login successful {form.email.data}', category= 'success')
            return render_template('Dashboard.html',title='Dashboard')
            # return redirect(url_for('homepage'))
        else:
            flash(f'login unsuccessful {form.email.data}', category= 'danger')
    return render_template('Lookin.html',titel='Lookin',form=form)

@app.route('/Reg',methods=['POST','GET'])      # done    REGISTER PAGE DELETE THIS LATER THIS IS NOT NEEDED 
def reg():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f'Account created {form.username.data}', category='success')
        return redirect(url_for('homepage'))
    return render_template('reg.html',titel='Reg',form=form)