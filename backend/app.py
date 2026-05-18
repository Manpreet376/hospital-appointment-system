from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Patient, Doctor, Department, Appointment, Prescription, Admin
from config import Config
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    role = session.get('role')
    if role == 'patient':
        return Patient.query.get(int(user_id))
    elif role == 'doctor':
        return Doctor.query.get(int(user_id))
    elif role == 'admin':
        return Admin.query.get(int(user_id))
    return None

@app.route('/')
def home():
    departments = Department.query.all()
    doctors_count = Doctor.query.count()
    patients_count = Patient.query.count()
    return render_template('index.html',
                           departments=departments,
                           doctors_count=doctors_count,
                           patients_count=patients_count)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        first_name  = request.form.get('first_name')
        last_name   = request.form.get('last_name')
        email       = request.form.get('email')
        password    = request.form.get('password')
        confirm     = request.form.get('confirm_password')
        phone       = request.form.get('phone')
        dob         = request.form.get('dob')
        gender      = request.form.get('gender')
        blood_group = request.form.get('blood_group')
        address     = request.form.get('address')
        if not all([first_name, last_name, email, password]):
            flash('Please fill all required fields.', 'error')
            return redirect(url_for('register'))
        if password != confirm:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))
        if Patient.query.filter_by(email=email).first():
            flash('Email already registered. Please login.', 'error')
            return redirect(url_for('register'))
        hashed_pw = generate_password_hash(password)
        patient = Patient(
            first_name=first_name, last_name=last_name,
            email=email, password=hashed_pw,
            phone=phone, dob=dob, gender=gender,
            blood_group=blood_group, address=address
        )
        db.session.add(patient)
        db.session.commit()
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email')
        password = request.form.get('password')
        role     = request.form.get('role', 'patient')
        user = None
        if role == 'patient':
            user = Patient.query.filter_by(email=email).first()
        elif role == 'doctor':
            user = Doctor.query.filter_by(email=email).first()
        elif role == 'admin':
            user = Admin.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['role'] = role
            login_user(user)
            if role == 'patient':
                return redirect(url_for('patient_dashboard'))
            elif role == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            elif role == 'admin':
                return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.pop('role', None)
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('home'))

@app.route('/doctors')
def doctors():
    dept_filter  = request.args.get('dept', '')
    search       = request.args.get('search', '')
    query        = Doctor.query
    if dept_filter:
        dept  = Department.query.filter_by(name=dept_filter).first()
        if dept:
            query = query.filter_by(department_id=dept.id)
    if search:
        query = query.filter(Doctor.name.ilike(f'%{search}%'))
    doctors_list = query.all()
    departments  = Department.query.all()
    return render_template('doctors.html',
                           doctors=doctors_list,
                           departments=departments,
                           selected_dept=dept_filter,
                           search=search)

@app.route('/book', methods=['GET', 'POST'])
@login_required
def book_appointment():
    if session.get('role') != 'patient':
        flash('Only patients can book appointments.', 'error')
        return redirect(url_for('home'))
    departments  = Department.query.all()
    doctors_list = Doctor.query.all()
    if request.method == 'POST':
        doctor_id = request.form.get('doctor_id')
        date      = request.form.get('date')
        time_slot = request.form.get('time_slot')
        reason    = request.form.get('reason')
        appt_type = request.form.get('appt_type', 'in-person')
        if not all([doctor_id, date, time_slot, reason]):
            flash('Please fill all fields.', 'error')
            return redirect(url_for('book_appointment'))
        appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=int(doctor_id),
            date=date, time_slot=time_slot,
            reason=reason, appt_type=appt_type,
            status='upcoming'
        )
        db.session.add(appointment)
        db.session.commit()
        flash('Appointment booked successfully!', 'success')
        return redirect(url_for('patient_dashboard'))
    selected_doctor = request.args.get('doctor_id')
    return render_template('book_appointment.html',
                           departments=departments,
                           doctors=doctors_list,
                           selected_doctor=selected_doctor)

@app.route('/patient/dashboard')
@login_required
def patient_dashboard():
    if session.get('role') != 'patient':
        return redirect(url_for('home'))
    appointments  = Appointment.query.filter_by(patient_id=current_user.id)\
                                     .order_by(Appointment.created_at.desc()).all()
    prescriptions = Prescription.query.filter_by(patient_id=current_user.id).all()
    upcoming   = [a for a in appointments if a.status == 'upcoming']
    completed  = [a for a in appointments if a.status == 'completed']
    cancelled  = [a for a in appointments if a.status == 'cancelled']
    return render_template('patient_dashboard.html',
                           appointments=appointments,
                           prescriptions=prescriptions,
                           upcoming_count=len(upcoming),
                           completed_count=len(completed),
                           cancelled_count=len(cancelled))

@app.route('/appointment/cancel/<int:appt_id>')
@login_required
def cancel_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if appt.patient_id != current_user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('patient_dashboard'))
    appt.status = 'cancelled'
    db.session.commit()
    flash('Appointment cancelled.', 'success')
    return redirect(url_for('patient_dashboard'))

@app.route('/patient/profile/update', methods=['POST'])
@login_required
def update_profile():
    current_user.first_name  = request.form.get('first_name')
    current_user.last_name   = request.form.get('last_name')
    current_user.phone       = request.form.get('phone')
    current_user.dob         = request.form.get('dob')
    current_user.gender      = request.form.get('gender')
    current_user.blood_group = request.form.get('blood_group')
    current_user.address     = request.form.get('address')
    db.session.commit()
    flash('Profile updated!', 'success')
    return redirect(url_for('patient_dashboard'))

@app.route('/doctor/dashboard')
@login_required
def doctor_dashboard():
    if session.get('role') != 'doctor':
        return redirect(url_for('home'))
    today       = datetime.today().strftime('%Y-%m-%d')
    today_appts = Appointment.query.filter_by(doctor_id=current_user.id, date=today).all()
    all_appts   = Appointment.query.filter_by(doctor_id=current_user.id).all()
    waiting     = [a for a in today_appts if a.status == 'upcoming']
    completed   = [a for a in today_appts if a.status == 'completed']
    return render_template('doctor_dashboard.html',
                           today_appts=today_appts,
                           all_appts=all_appts,
                           waiting_count=len(waiting),
                           completed_count=len(completed),
                           today=today)

@app.route('/appointment/done/<int:appt_id>')
@login_required
def mark_done(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if appt.doctor_id != current_user.id:
        flash('Unauthorized.', 'error')
        return redirect(url_for('doctor_dashboard'))
    appt.status = 'completed'
    db.session.commit()
    flash('Marked as completed!', 'success')
    return redirect(url_for('doctor_dashboard'))

@app.route('/prescription/write/<int:appt_id>', methods=['GET', 'POST'])
@login_required
def write_prescription(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    if request.method == 'POST':
        presc = Prescription(
            appointment_id=appt_id,
            patient_id=appt.patient_id,
            doctor_id=current_user.id,
            diagnosis=request.form.get('diagnosis'),
            medicines=request.form.get('medicines'),
            notes=request.form.get('notes'),
            followup_date=request.form.get('followup_date')
        )
        db.session.add(presc)
        db.session.commit()
        flash('Prescription saved!', 'success')
        return redirect(url_for('doctor_dashboard'))
    return render_template('prescription.html', appt=appt)

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
    today = datetime.today().strftime('%Y-%m-%d')
    return render_template('admin_dashboard.html',
        total_doctors=Doctor.query.count(),
        total_patients=Patient.query.count(),
        total_appts=Appointment.query.count(),
        today_appts=Appointment.query.filter_by(date=today).count(),
        completed_today=Appointment.query.filter_by(date=today, status='completed').count(),
        all_appointments=Appointment.query.order_by(Appointment.created_at.desc()).limit(20).all(),
        all_doctors=Doctor.query.all(),
        all_patients=Patient.query.all(),
        departments=Department.query.all()
    )

@app.route('/admin/doctor/add', methods=['POST'])
@login_required
def add_doctor():
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
    name    = request.form.get('name')
    email   = request.form.get('email')
    dept_id = request.form.get('department_id')
    spec    = request.form.get('specialization')
    exp     = request.form.get('experience')
    fee     = request.form.get('fee', 500)
    if Doctor.query.filter_by(email=email).first():
        flash('Email already exists.', 'error')
        return redirect(url_for('admin_dashboard'))
    doctor = Doctor(
        name=name, email=email,
        password=generate_password_hash('doctor123'),
        specialization=spec, experience=exp,
        department_id=int(dept_id), fee=int(fee)
    )
    db.session.add(doctor)
    db.session.commit()
    flash(f'{name} added! Default password: doctor123', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/doctor/delete/<int:doctor_id>')
@login_required
def delete_doctor(doctor_id):
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
    doctor = Doctor.query.get_or_404(doctor_id)
    db.session.delete(doctor)
    db.session.commit()
    flash('Doctor removed.', 'success')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/appointment/delete/<int:appt_id>')
@login_required
def delete_appointment(appt_id):
    if session.get('role') != 'admin':
        return redirect(url_for('home'))
    appt = Appointment.query.get_or_404(appt_id)
    db.session.delete(appt)
    db.session.commit()
    flash('Appointment deleted.', 'success')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database tables created!")
    app.run(debug=True)