from flask import current_app as app
from flask import render_template,request,redirect,url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from models import *
from datetime import datetime,timedelta

# will impliment flash func later in the html files

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
                if user.tStaffs[0].status == 1:
                    login_user(user) 
                    return redirect(url_for('ts_dashboard', id=user.id))
                else:
                    flash('WAIT!! Admin is approving your account.')
                    return redirect(url_for('signin'))
            elif user.role==2:
                login_user(user)
                return redirect(url_for('tr_dashboard', id=user.id))

        flash("Invalid email or password!")   
        return redirect(url_for('signin'))
    return render_template("login.html")


@app.route("/register", methods=["GET","POST"])
def signup():
    if request.method=="POST":
        mail=request.form.get("emailid")
        pwd=request.form.get("pwd") 
        role=request.form.get("utype")
        user=db.session.query(User).filter(User.email==mail).first()
        if user:
            return render_template("signup.html",err_msg="Email already in use!")
        newUser=User(email=mail,password=pwd,role=int(role))
        db.session.add(newUser)
        db.session.commit()
        fname=request.form.get("fname")
        address=request.form.get("address")
        phno=request.form.get("phno")
        if int(role)==2:
            tr_profile=Tr_Profile(trID=newUser.id,full_name=fname,address=address,phno=phno, status=0)
            db.session.add(tr_profile)
        else:
            # HERE
            # HERE
            ts_profile=Ts_Profile(tsID=newUser.id,full_name=fname,address=address,phno=phno, status=0) # HERE
            db.session.add(ts_profile)
        db.session.commit()
        return redirect(url_for("signin"))
    return render_template("signup.html")

@app.route('/logout')
@login_required
def logout():
    logout_user() #delete from session
    return redirect(url_for('signin'))

'''
    #### Routes defined for admin dashboard ####
'''
@app.route("/admin")
@login_required
def admin_dashboard():
    if current_user.role != 0:
        return redirect(url_for('home'))
    total_treks = Trek.query.count()
    total_users = User.query.filter(User.role ==2).count()
    total_staff = User.query.filter(User.role==1).count()
    total_bookings=Booking.query.count()
    pending_staff = Ts_Profile.query.filter_by(status=0).all()
    all_treks = Trek.query.all()

    return render_template('admin_dashboard.html', total_treks=total_treks, total_users=total_users, total_staff=total_staff, total_bookings=total_bookings, pending_staff=pending_staff, all_treks=all_treks)

@app.route("/admin/approve_ts/<int:ts_id>")
@login_required
def approve_ts(ts_id):
    if current_user.role == 0:
        staff=Ts_Profile.query.get(ts_id)
        if staff:
            staff.status = 1
            db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/create_tk', methods=['GET', 'POST'])
@login_required
def create_trek():
    if current_user.role != 0:
        return redirect(url_for('home'))
    if request.method == 'POST':
        name= request.form.get('name')
        location= request.form.get('location')
        duration=request.form.get('duration')
        difficulty=request.form.get('difficulty')
        slots = request.form.get('slots')
        ts_id =request.form.get('ts_id')
        start_dt_str =request.form.get('start_dt') # LATER
        end_dt_str =request.form.get('end_dt') # LATER
        start_dt = datetime.strptime(start_dt_str, '%Y-%m-%d').date()
        end_dt = datetime.strptime(end_dt_str, '%Y-%m-%d').date()
        new_trek =Trek(name=name, location=location, duration=duration, difficulty=difficulty,slots=slots, ts_id=ts_id, start_dt=start_dt, end_dt=end_dt, status='Approved') # LATER status
        db.session.add(new_trek)
        db.session.commit()
        return redirect(url_for('admin_dashboard'))
    staff_list = Ts_Profile.query.filter_by(status=1).all()
    return render_template('create_tk.html', staff_list=staff_list)

@app.route('/ts/<int:id>')
@login_required
def ts_dashboard(id):
    if current_user.role != 1:
        return redirect(url_for('home'))
    staff_profile = Ts_Profile.query.filter_by(tsID=current_user.id).first()
    assigned_treks = Trek.query.filter_by(ts_id=staff_profile.id).all()
    return render_template('ts_dashboard.html', staff=staff_profile, treks=assigned_treks)

@app.route('/ts/tkStatus/<int:trek_id>', methods=['GET','POST'])
@login_required
def update_tkStatus(trek_id):
    newStatus = request.form.get('status')
    tk = Trek.query.get(trek_id)
    if tk and tk.staff.tsID == current_user.id:
        tk.status = newStatus 
        db.session.commit()
    return redirect(url_for('ts_dashboard', id=current_user.id))


@app.route('/tr/<int:id>')
@login_required
def tr_dashboard(id):
    if current_user.role != 2:
        return redirect(url_for('home'))
    open_treks = Trek.query.filter_by(status='Open').all()
    user_bookings= Booking.query.filter_by(tr_id = current_user.id).all()
    return render_template('tr_dashboard.html', open_treks=open_treks, bookings=user_bookings)

@app.route('/book_tk/<int:trek_id>', methods=['GET', 'POST'])
@login_required 
def book_trek(trek_id):
    if current_user.role != 2:
        return redirect(url_for('home'))
    tk = Trek.query.get(trek_id)
    if tk.status == 'Open' and tk.slots > 0:
        existing_booking = Booking.query.filter_by(tk_id=tk.id).first()
        if not existing_booking:
            booking_time = request.form.get('booking_time')
            new_booking = Booking(tk_id=tk.id, tr_id=current_user.id, booking_time= datetime.utcnow()) # LATER
            tk.slots -=1
            db.session.add(new_booking)
            db.session.commit()
    return redirect(url_for('tr_dashboard', id=current_user.id))