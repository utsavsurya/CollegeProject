from codelearn_flask import app,db #,conn
from codelearn_flask.models import Datas
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
from sklearn.linear_model import LinearRegression

DB_HOST = "192.168.1.7"
DB_NAME = "iot_db"
DB_USER = "project"
DB_PASS = "123456"

def log_to_db(request_data):
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
    return "off"

def data_to_dashboard():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    cur.execute('SELECT temperature FROM datas ORDER BY "time" DESC LIMIT 1')
    t = cur.fetchall()
    cur.execute('SELECT humidity FROM datas ORDER BY "time" DESC LIMIT 1')
    h = cur.fetchall()
    cur.execute('SELECT water FROM datas ORDER BY "time" DESC LIMIT 1')
    w = cur.fetchall()
    cur.close()

    Temperature = t[0]
    Humidity = h[0]
    Water = w[0]

    data = [time() * 1000, Temperature[0] , Humidity[0], Water[0]]
    return data

def data_for_1day_graph():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    cur.execute("SELECT time,temperature,humidity,water FROM datas where time > now() - interval '1 day';")
    t = cur.fetchall()
    cur.close()

    Datetime = pd.DataFrame([int(row[0].strftime("%H")) for row in t],columns=['hour'])
    Temperature = pd.DataFrame([row[1] for row in t],columns=['Temp'])
    Humidity = pd.DataFrame([row[2] for row in t],columns=['Hum'])
    Water = pd.DataFrame([row[3] for row in t],columns=['Wat'])
    data = pd.DataFrame(pd.concat([Datetime,Temperature,Humidity,Water],axis=1))
    return data

def data_for_1hour_graph():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    cur.execute("SELECT time,temperature,humidity FROM datas where time > now() - interval '1 hour';")
    t = cur.fetchall()
    cur.close()

    Datetime = pd.DataFrame([int(row[0].strftime("%M")) for row in t],columns=['Minute'])
    Temperature = pd.DataFrame([row[1] for row in t],columns=['Temp'])
    Humidity = pd.DataFrame([row[2] for row in t],columns=['Hum'])
    data = pd.DataFrame(pd.concat([Datetime,Temperature,Humidity],axis=1))
    return data

def data_for_1week_graph():
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    cur.execute("SELECT time,temperature,humidity FROM datas where time > now() - interval '1 week';")
    t = cur.fetchall()
    cur.close()

    Datetime = pd.DataFrame([(row[0].strftime("%A")) for row in t],columns=['day'])
    Temperature = pd.DataFrame([row[1] for row in t],columns=['Temp'])
    Humidity = pd.DataFrame([row[2] for row in t],columns=['Hum'])    
    data = pd.DataFrame(pd.concat([Datetime,Temperature,Humidity],axis=1))
    return data

def ML_predict(hour , minute):
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    cur = conn.cursor()
    cur.execute("SELECT time,temperature,humidity FROM datas where time > now() - interval '1 month';")
    t = cur.fetchall()
    cur.close()

    Minute = pd.DataFrame([int(row[0].strftime("%H")) for row in t],columns=['Minute'])
    Hour = pd.DataFrame([int(row[0].strftime("%M")) for row in t],columns=['Hour'])
    Temperature = pd.DataFrame([row[1] for row in t],columns=['Temp'])
    Humidity = pd.DataFrame([row[2] for row in t],columns=['Hum'])    
    data = pd.DataFrame(pd.concat([Hour,Minute,Temperature,Humidity],axis=1))
    data.dropna(inplace=True)
    data[data["Hum"]==np.nan]
    data
    X = data[["Hour","Minute"]]
    y = data[["Temp","Hum"]]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=1)

    lm = LinearRegression()
    lm.fit(X_train,y_train)

    predictions = list(lm.predict(pd.DataFrame([[hour,minute]])))
    return predictions[0]