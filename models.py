from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
db=SQLAlchemy()

class User(db.Model,UserMixin):
    __tablename__='users'
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    role=db.Column(db.Integer,nullable=False) #0/1/2
    trekkers=db.relationship("Tr_Profile",cascade="all,delete",backref='users')
    tStaffs=db.relationship("Ts_Profile",cascade="all,delete",backref='users')
    #CHECK



class Tr_Profile(db.Model):
    __tablename__='tr_profile'
    id=db.Column(db.Integer,primary_key=True)
    trID=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    full_name=db.Column(db.String,nullable=False)
    address=db.Column(db.String,nullable=False)
    phno=db.Column(db.String,nullable=False)
    status=db.Column(db.Integer,nullable=False,default=0) #0-register, 1-deactivated


class Ts_Profile(db.Model):
    __tablename__='ts_profile'
    id=db.Column(db.Integer,primary_key=True)
    tsID=db.Column(db.Integer,db.ForeignKey('users.id'),nullable=False)
    full_name=db.Column(db.String,nullable=False)
    phno=db.Column(db.String,nullable=False)
    address=db.Column(db.String,nullable=False)
    #CHECK
    #CHECK
    status=db.Column(db.Integer,nullable=False,default=0) #0-register, 1-approved, 2-deactivated
