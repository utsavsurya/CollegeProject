from codelearn_flask import db
from datetime import datetime


class Datas(db.Model):
    time           = db.Column(db.DateTime,default=datetime.utcnow,primary_key=True)
    temperature    = db.Column(db.Float,nullable=True)
    water          = db.Column(db.Float,nullable=True)
    no_of_people   = db.Column(db.Integer,nullable=True)
    power          = db.Column(db.Float,nullable=True)
    humidity       = db.Column(db.Float,nullable=True)
    

def __repr_(self):
    return f'{self.time}:{self.temperature}:{self.humidity}:{self.water}:{self.power}:{self.no_of_people}'