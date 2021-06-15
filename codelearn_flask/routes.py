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
import numpy as np
import pandas as pd

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
    cur.execute('SELECT water FROM datas ORDER BY "time" DESC LIMIT 1')
    t = cur.fetchall()
    cur.close()
    water = t[0][0]
    air = 100-water
    waterdata = [water,air]
    return render_template('Dashboard.html',title='Dashboard',water_data=waterdata)
 
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
        return "Led on"
    if request.method == "GET":
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cur = conn.cursor()
        cur.execute("SELECT time,temperature,humidity FROM datas where time > now() - interval '1 hour';")
        t = cur.fetchall()
        cur.close()

        labels = [int(row[0].strftime("%M")) for row in t]
        Temperature = [row[1] for row in t]
        Humidity = [row[2] for row in t]
        
        return render_template('ML.html',labels=labels,values1=Temperature,values2=Humidity)
    # return render_template('DataBoard.html',title='DataBoard')

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

@app.route('/test', methods=["GET", "POST"])   # FOR EXPERIMENTING PURPOUS ONLY
def test():
    return render_template("MLpage.html",titel='Lookin')
    
@app.route('/oneday',methods=['GET'])          # SENDS HOURLY DATA TO WEBPAGE
def oneday():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    cur.execute("SELECT time,temperature,humidity FROM datas where time > now() - interval '1 day';")
    t = cur.fetchall()
    cur.close()

    Datetime = pd.DataFrame([int(row[0].strftime("%H")) for row in t],columns=['hour'])
    Temperature = pd.DataFrame([row[1] for row in t],columns=['Temp'])
    Humidity = pd.DataFrame([row[2] for row in t],columns=['Hum'])
    data = pd.DataFrame(pd.concat([Datetime,Temperature,Humidity],axis=1))
    time = list(data["hour"].unique())
    dd = data.groupby("hour").mean()
    return render_template('oneday.html',labels=time,values1=list(dd["Temp"]),values2=list(dd["Hum"]))

@app.route('/onehour',methods=['GET'])       # SENDS EVERY MINUTE DATA TO WEBPAGE
def onehour():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    cur.execute("SELECT time,temperature,humidity FROM datas where time > now() - interval '1 hour';")
    t = cur.fetchall()
    cur.close()

    Datetime = pd.DataFrame([int(row[0].strftime("%M")) for row in t],columns=['Minute'])
    Temperature = pd.DataFrame([row[1] for row in t],columns=['Temp'])
    Humidity = pd.DataFrame([row[2] for row in t],columns=['Hum'])
    data = pd.DataFrame(pd.concat([Datetime,Temperature,Humidity],axis=1))
    time = list(data["Minute"].unique())
    dd = data.groupby("Minute").mean()
    return render_template('onehour.html',labels=time,values1=list(dd["Temp"]),values2=list(dd["Hum"]))

@app.route('/oneweek',methods=['GET'])       # SENDS DAILY DATA TO WEBPAGE
def oneweek():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    cur.execute("SELECT time,temperature,humidity FROM datas where time > now() - interval '1 week';")
    t = cur.fetchall()
    cur.close()

    Datetime = pd.DataFrame([(row[0].strftime("%A")) for row in t],columns=['day'])
    Temperature = pd.DataFrame([row[1] for row in t],columns=['Temp'])
    Humidity = pd.DataFrame([row[2] for row in t],columns=['Hum'])    
    data = pd.DataFrame(pd.concat([Datetime,Temperature,Humidity],axis=1))
    time = list(data["day"].unique())
    dd = data.groupby("day").mean()
    return render_template('oneweek.html',labels=time,values1=list(dd["Temp"]),values2=list(dd["Hum"]))

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

@app.route('/predict',methods=['POST','GET']) # done  WHERE DATA FROM ARDUNIO IS COMMING VIA POST METHOD AND NEED TO BE HANDLED AND PUT INTO DATA BASE
def predict():
    Hour = int(request.args.get('time')[0:2])
    Minute = int(request.args.get('time')[3:5])
    return '''
              <h1>The Hour value is: {}</h1>
              <h1>The Minute value is: {}</h1>'''.format(Hour, Minute)

@app.route('/voice',methods=['POST','GET']) # done  WHERE DATA FROM ARDUNIO IS COMMING VIA POST METHOD AND NEED TO BE HANDLED AND PUT INTO DATA BASE
def voice():
    com = request.args.get('command')
    if com == "LED on":
        return "on"
    else:
        return "off"