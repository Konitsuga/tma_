from flask import current_app as app
from flask import render_template,request,redirect,url_for
from flask_login import login_user, logout_user, login_required, current_user
from models import *
from datetime import datetime,timedelta

@app.route("/")
def home():
    return render_template('home.html')

@app.route("/login",methods=["GET","POST"])
def signin():
    if request.method=="POST":
        mail=request.form.get("emailid")
        pwd=request.form.get("pwd")
        user=db.session.query(User).filter(User.email==mail,User.password==pwd).first()
        if user:
            if user.role==0:
                login_user(user)
                return redirect(url_for("admin_dashboard"))
            elif user.role==1:
                login_user(user) 
                return render_template("ts_dashboard.html",id=user.id)
            elif user.role==2:
                login_user(user)
                return redirect(url_for("tr_dashboard",id=user.id))
            
        return redirect(url_for('signup'))
    return render_template("login.html")


@app.route("/register", methods=["GET","POST"])
def signup():
    if request.method=="POST":
        mail=request.form.get("emailid") #data from front end form
        pwd=request.form.get("pwd") 
        role=request.form.get("utype")
        user=db.session.query(User).filter(User.email==mail).first() #check existence/uniqueness
        if user:
            return render_template("signup.html",err_msg="Email already in use!")
        else:
            newUser=User(email=mail,password=pwd,role=int(role))
            db.session.add(newUser)
            db.session.commit()
            fname=request.form.get("fname")
            address=request.form.get("address")
            phno=request.form.get("phno")
            if int(role)==2:
                tr_profile=Tr_Profile(trID=newUser.id,full_name=fname,address=address,phno=phno)
                db.session.add(tr_profile) #if it patient role
            else:
                #CHECK HERE
                #CHECK HERE
                ts_profile=Ts_Profile(tsID=newUser.id,full_name=fname,address=address,phno=phno) #CHECK
                db.session.add(ts_profile)
            db.session.commit()
            return redirect(url_for("signin"))
    else:
        return render_template("signup.html")

@app.route('/logout')
def logout():
    logout_user() #delete from session
    return redirect(url_for('signin'))
