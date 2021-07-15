from codelearn_flask import app,conn #,db 
from flask import render_template,url_for,redirect,flash,request,make_response
from codelearn_flask.forms import RegistrationForm,LoginForm
from codelearn_flask.models import Datas
from codelearn_flask.functions import log_to_db,data_to_dashboard,data_for_1day_graph,data_for_1hour_graph,data_for_1week_graph,ML_predict
import json
from time import time
from random import random         # remove later
import psycopg2
import psycopg2.extras
import datetime
import pytz
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

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
    water = ((t[0][0])/575)*100
    air = 100-water
    waterdata = [water,air]
    return render_template('Dashboard.html',title='Dashboard',water_data=waterdata)

@app.route('/DataBoard',methods=['POST','GET']) # done  WHERE DATA FROM ARDUNIO IS COMMING VIA POST METHOD AND NEED TO BE HANDLED AND PUT INTO DATA BASE
def upload():
    if request.method == "POST":
        return log_to_db(request.get_json())


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
    response = make_response(json.dumps(
        data_to_dashboard()                 # function where data is comming from
        ))
    response.content_type = 'application/json'
    return response

@app.route('/test', methods=["GET", "POST"])   # FOR EXPERIMENTING PURPOUS ONLY
def test():
    return render_template("MLpage.html",titel='Lookin')
    
@app.route('/oneday',methods=['GET'])          # SENDS HOURLY DATA TO WEBPAGE
def oneday():
    data = data_for_1day_graph()           # from functons.py
    time = list(data["hour"].unique())
    dd = data.groupby("hour").mean()
    return render_template('oneday.html',labels=time,values1=list(dd["Temp"]),values2=list(dd["Hum"]),water_values=list(dd["Wat"]))

@app.route('/onehour',methods=['GET'])       # SENDS EVERY MINUTE DATA TO WEBPAGE
def onehour():
    data = data_for_1hour_graph()
    time = list(data["Minute"].unique())
    dd = data.groupby("Minute").mean()
    return render_template('onehour.html',labels=time,values1=list(dd["Temp"]),values2=list(dd["Hum"]))

@app.route('/oneweek',methods=['GET'])       # SENDS DAILY DATA TO WEBPAGE
def oneweek():
    data = data_for_1week_graph()
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
    data = ML_predict(Hour,Minute)
    # cur = conn.cursor()
    # cur.execute("SELECT time,temperature,humidity FROM datas where time > now() - interval '1 month';")
    # t = cur.fetchall()
    # cur.close()

    # Minute = pd.DataFrame([int(row[0].strftime("%H")) for row in t],columns=['Minute'])
    # Hour = pd.DataFrame([int(row[0].strftime("%M")) for row in t],columns=['Hour'])
    # Temperature = pd.DataFrame([row[1] for row in t],columns=['Temp'])
    # Humidity = pd.DataFrame([row[2] for row in t],columns=['Hum'])    
    # data = pd.DataFrame(pd.concat([Hour,Minute,Temperature,Humidity],axis=1))
    # data.dropna(inplace=True)
    # data[data["Hum"]==np.nan]
    # data
    # X = data[["Hour","Minute"]]
    # y = data[["Temp","Hum"]]   
     

    return '''
              <h1>The predected Temperature value is: {}</h1>
              <h1>The predected Humidity value is: {}</h1>'''.format(data[0], data[1])

@app.route('/voice',methods=['POST','GET']) # done  WHERE DATA FROM ARDUNIO IS COMMING VIA POST METHOD AND NEED TO BE HANDLED AND PUT INTO DATA BASE
def voice():
    if request.method == "POST":
        com = request.args.get('command')
        day_mode = 0
        night_mode = 0
        party_mode = 0
        movie_mode = 0
        if com == "good morning" or com == "LED on" or com == "day mode" :
            day_mode = 1
        
        elif com == "good night" or com == "led off" or com == "night mode" :
            night_mode = 1
    
        elif com == "let's party" or com == "party mode" :
            party_mode = 1
    
        elif com == "movie time" or com == "let's watch a movie" :
            movie_mode = 1
    
        if day_mode ==1 or night_mode ==1 or party_mode ==1 or movie_mode ==1:
            conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
            cur = conn.cursor()
            cur.execute("INSERT INTO activitylog VALUES (%s, %s, %s, %s, %s);",
                            (  
                                datetime.datetime.now(pytz.timezone('Asia/Kolkata')),
                                day_mode,
                                night_mode,
                                party_mode,
                                movie_mode,
                            ),
                        )
            conn.commit()
            cur.close()
    if request.method == "GET":
        conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        cur = conn.cursor()
        cur.execute('SELECT daymode,nightmode,partymode,moviemode FROM activitylog ORDER BY "Time" DESC LIMIT 1')
        t = cur.fetchall()
        cur.close()
        status = list(t[0])        
        return {"day_mode":status[0],"night_mode":status[1],"party_mode":status[2],"movie_mode":status[3]}

@app.route("/todo",methods=["POST","GET"])
def home():
    if request.method == "POST":
        todo = request.form.get("todo")
        print(todo)
    return render_template('MLpage.html')