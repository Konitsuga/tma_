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
                elif user.tStaffs[0].status == 2:
                    flash('Your account has been deactivated by Admin.')
                    return redirect(url_for('signin'))
                else:
                    flash('WAIT!! Admin is approving your account.')
                    return redirect(url_for('signin'))
            elif user.role==2:
                if user.trekkers[0].status == 0:
                    login_user(user)
                    return redirect(url_for('tr_dashboard', id=user.id))
                else:
                    flash('Your account has been deactivated by Admin.')
                    return redirect(url_for('signin'))

        flash("Invalid email or password!")   
        return redirect(url_for('signin'))
    return render_template("login.html")

@app.route('/profile')
@login_required
def view_profile():
    if current_user.role == 1:
        pf= Ts_Profile.query.filter_by(tsID=current_user.id).first()
    elif current_user.role == 2:
        pf = Tr_Profile.query.filter_by(trID=current_user.id).first()
        
    return render_template('profile.html', pf=pf)

@app.route('/edit_pf', methods=['GET', 'POST'])
@login_required
def edit_pf():
    if current_user.role == 1:
        pf = Ts_Profile.query.filter_by(tsID=current_user.id).first()
    elif current_user.role == 2:
        pf = Tr_Profile.query.filter_by(trID=current_user.id).first()
    if request.method == 'POST':
        if pf:
            pf.full_name = request.form.get('full_name')
            pf.phno = request.form.get('phno')
            pf.address = request.form.get('address')
        new_pwd = request.form.get('pwd')
        if new_pwd:
            current_user.password = new_pwd   
        db.session.commit()
        flash("Profile updated sucessfully!")
        if current_user.role == 1:
            return redirect(url_for('ts_dashboard', id=current_user.id))
        elif current_user.role == 1:
            return redirect(url_for('tr_dashboard', id=current_user.id))

    return render_template('edit_pf.html', pf=pf)

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
    all_tks = Trek.query.all()
    all_tr = Tr_Profile.query.all()
    all_ts = Ts_Profile.query.filter(Ts_Profile.status != 0).all()

    return render_template('admin_dashboard.html', total_treks=total_treks, total_users=total_users, total_staff=total_staff, total_bookings=total_bookings, pending_staff=pending_staff, all_tks=all_tks, all_tr=all_tr, all_ts=all_ts)

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

@app.route('/admin/toggle_ts/<int:ts_id>')
@login_required
def toggle_ts(ts_id):
    if current_user.role != 0:
        return redirect(url_for('home'))
    
    ts = Ts_Profile.query.get(ts_id)
    if ts:
        if ts.status == 1:
            ts.status = 2
            flash(f"Staff {ts.full_name} deactivated.")
        elif ts.status == 2:
            ts.status = 1
            flash(f"Staff {ts.full_name} reactivated.")
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/toggle_tr/<int:tr_id>')
@login_required
def toggle_tr(tr_id):
    if current_user.role != 0:
        return redirect(url_for('home'))
        
    tr = Tr_Profile.query.get(tr_id)
    if tr:
        if tr.status == 0:
            tr.status = 1
            flash(f"Trekker {tr.full_name} deactivated.")
        elif tr.status == 1:
            tr.status = 0
            flash(f"Trekker {tr.full_name} reactivated.")
        db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/search', methods=['GET'])
@login_required
def admin_search():
    if current_user.role != 0:
        return redirect(url_for('home'))

    # (?searchtxt=3) LOOK
    search = request.args.get('searchtxt', '')
    
    if not search:
        flash("Type to Search")
        return redirect(url_for('admin_dashboard'))

    search_tks = Trek.query.filter(
        (Trek.name.ilike(f'%{search}%')) | 
        (Trek.location.ilike(f'%{search}%'))).all()

    search_ts = Ts_Profile.query.filter(
        (Ts_Profile.full_name.ilike(f'%{search}%')) |
        (Ts_Profile.phno.ilike(f'%{search}%'))).all()

    search_trs = Tr_Profile.query.filter(
        (Tr_Profile.full_name.ilike(f'%{search}%')) |
        (Tr_Profile.phno.ilike(f'%{search}%'))).all()

    return render_template('admin_search.html', query=search, tks=search_tks, ts=search_ts, trs=search_trs)

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
    booked_tkIDs = [booking.tk_id for booking in user_bookings]
    return render_template('tr_dashboard.html', open_treks=open_treks, bookings=user_bookings, booked_tkIDs=booked_tkIDs)

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

@app.route('/edit_tk/<int:tk_id>', methods=['GET', 'POST'])
@login_required
def edit_trek(tk_id):
    tk = Trek.query.get(tk_id)
    if not tk:
        flash("Trek not found.")
        return redirect(url_for('home'))
    is_admin = (current_user.role == 0)
    is_assigned_ts = (current_user.role == 1 and current_user.tStaffs and tk.ts_id == current_user.tStaffs[0].id)
    
    if not (is_admin or is_assigned_ts):
        flash("Unauthorized to edit this trek.")
        return redirect(url_for('home'))

    if request.method == 'POST':
        tk.slots = request.form.get('slots')
        if is_admin:
            tk.name = request.form.get('name')
            tk.location = request.form.get('location')
            tk.duration = request.form.get('duration')
            tk.difficulty = request.form.get('difficulty')
            
            start_dt_str = request.form.get('start_dt')
            end_dt_str = request.form.get('end_dt')
            if start_dt_str:
                tk.start_dt = datetime.strptime(start_dt_str, '%Y-%m-%d').date()
            if end_dt_str:
                tk.end_dt = datetime.strptime(end_dt_str, '%Y-%m-%d').date()
                
            new_ts_id = request.form.get('ts_id')
            if new_ts_id:
                tk.ts_id = new_ts_id
        db.session.commit()
        flash(f"Trek updated successfully!!!")   
        return redirect(url_for('edit_trek', tk_id=tk.id))
    ts_list = Ts_Profile.query.filter_by(status=1).all() if is_admin else []
    return render_template('edit_tk.html', tk=tk, is_admin=is_admin, ts_list=ts_list)

@app.route('/update_booking/<int:booking_id>', methods=['POST'])
@login_required
def update_booking(booking_id):
    booking = Booking.query.get(booking_id)
    if not booking:
        return redirect(request.referrer)
    is_admin = (current_user.role == 0)
    is_assigned_ts = (current_user.role == 1 and current_user.tStaffs and booking.treks.ts_id == current_user.tStaffs[0].id)
    if is_admin or is_assigned_ts:
        new_status = request.form.get('status')
        if new_status == 'Cancelled' and booking.status != 'Cancelled':
            booking.treks.slots += 1
        elif booking.status == 'Cancelled' and new_status != 'Cancelled':
            booking.treks.slots -= 1    
        booking.status = new_status
        db.session.commit()
        flash(f"Participant currentstatus is {new_status}.")
    else:
        flash("unauthorized!!!")
        
    return redirect(request.referrer)