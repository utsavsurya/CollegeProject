from codelearn_flask import app,db #,conn
from codelearn_flask.models import Datas


def log_to_db(request_data):    
    temp  = request_data['temp']
    hum   = request_data['hum']
    wat   = request_data['water']
    powr  = request_data['pow']
    ppl   = request_data['ppl']
    data  = Datas(temperature=temp,humidity=hum,water=wat,power=powr,no_of_people=ppl)
    db.session.add(data)
    db.session.commit()

def temp_last_value():
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT temperature FROM datas;")
            last_val = curser.fetchall()
    return last_val[-1]

def hum_last_value():
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT humidity FROM datas;")
            last_val = curser.fetchall()
    return last_val[-1]