from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import psycopg2

app=Flask(__name__)

import psycopg2
import psycopg2.extras

DB_HOST = "192.168.1.7"
DB_NAME = "iot_db"
DB_USER = "project"
DB_PASS = "123456"
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

app.config['SECRET_KEY']="myiotproject"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://project:123456@localhost:5432/iot_db'

db = SQLAlchemy(app)                        # this will initilize databasefiles inside sqlalchmy
from codelearn_flask import routes