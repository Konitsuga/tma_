from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin
db=SQLAlchemy()

# bk=booking, tk=trek, tr=trekker, ts=tStaff, 


class User(db.Model,UserMixin):
    __tablename__='user'
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    role=db.Column(db.Integer,nullable=False) #0/1/2
    trekkers=db.relationship("Tr_Profile",cascade="all,delete",backref='users')
    tStaffs=db.relationship("Ts_Profile",cascade="all,delete",backref='users')


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
    status=db.Column(db.Integer,nullable=False,default=0) #0-register, 1-approved, 2-deactivated, 3-open, 4-full


class booking(db.Model):
    __tablename__='booking'
    id=db.Column(db.Integer,primary_key=True)
    ts_id=db.Column(db.Integer,db.ForeignKey('ts_profile.id'),nullable=False)
    tr_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    token_no=db.Column(db.Integer,nullable=False)
    booking_time=db.Column(db.String,nullable=False)
    status=db.Column(db.String,default='b') #b-booked,d-completed,c-cancelled

    treks=db.relationship("Trek",cascade="all,delete",backref='bookings') 


class Trek(db.Model):
    __tablename__='trek'
    id=db.Column(db.Integer,primary_key=True)
    bk_id=db.Column(db.Integer,db.ForeignKey('booking.id'),nullable=False)
    name = db.Column(db.String, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False, default=0)
    dt_time=db.Column(db.String,nullable=False)
    status = db.Column(db.String, nullable=False, default='0') # 0/1/2/3/4
    slots = db.Column(db.Integer, nullable=False)
    details=db.Column(db.String,nullable=True)

# User (role: Admin / Trek Staff / Trekker)
# Trek (Trek Name, Difficulty, Duration, Available Slots, Assigned Staff, Status, etc)
# Booking ( User ID, Trek ID, Booking Status, Booking Date, Payment Status, etc )
# Maintain proper trek status tracking (Pending / Approved / Open / Closed / Completed).
# Update trek status (Open/Closed).
