from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

# ── PATIENT ──
class Patient(UserMixin, db.Model):
    __tablename__ = 'patients'
    id           = db.Column(db.Integer, primary_key=True)
    first_name   = db.Column(db.String(50), nullable=False)
    last_name    = db.Column(db.String(50), nullable=False)
    email        = db.Column(db.String(100), unique=True, nullable=False)
    password     = db.Column(db.String(200), nullable=False)
    phone        = db.Column(db.String(15))
    dob          = db.Column(db.String(20))
    gender       = db.Column(db.String(10))
    blood_group  = db.Column(db.String(5))
    address      = db.Column(db.String(200))
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    appointments = db.relationship('Appointment', backref='patient', lazy=True)

    def full_name(self):
        return f"{self.first_name} {self.last_name}"

# ── DEPARTMENT ──
class Department(db.Model):
    __tablename__ = 'departments'
    id      = db.Column(db.Integer, primary_key=True)
    name    = db.Column(db.String(100), unique=True, nullable=False)
    emoji   = db.Column(db.String(5), default='🏥')
    doctors = db.relationship('Doctor', backref='department', lazy=True)

# ── DOCTOR ──
class Doctor(db.Model):
    __tablename__ = 'doctors'
    id            = db.Column(db.Integer, primary_key=True)
    name          = db.Column(db.String(100), nullable=False)
    email         = db.Column(db.String(100), unique=True, nullable=False)
    password      = db.Column(db.String(200), nullable=False)
    specialization = db.Column(db.String(100))
    experience    = db.Column(db.String(30))
    availability  = db.Column(db.String(100), default='Mon-Fri, 10am-4pm')
    fee           = db.Column(db.Integer, default=500)
    status        = db.Column(db.String(20), default='available')
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    appointments  = db.relationship('Appointment', backref='doctor', lazy=True)

    # ── YEH 4 LINES ADD KARO ──
    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def initials(self):
        parts = self.name.split()
        return ''.join(p[0] for p in parts if p[0].isupper())[:2]

# ── APPOINTMENT ──
class Appointment(db.Model):
    __tablename__ = 'appointments'
    id         = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.id'), nullable=False)
    doctor_id  = db.Column(db.Integer, db.ForeignKey('doctors.id'),  nullable=False)
    date       = db.Column(db.String(20), nullable=False)
    time_slot  = db.Column(db.String(20), nullable=False)
    reason     = db.Column(db.String(300))
    appt_type  = db.Column(db.String(20), default='in-person')
    status     = db.Column(db.String(20), default='upcoming')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ── PRESCRIPTION ──
class Prescription(db.Model):
    __tablename__ = 'prescriptions'
    id             = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    patient_id     = db.Column(db.Integer, db.ForeignKey('patients.id'))
    doctor_id      = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    diagnosis      = db.Column(db.String(200))
    medicines      = db.Column(db.Text)
    notes          = db.Column(db.Text)
    followup_date  = db.Column(db.String(20))
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

# ── ADMIN ──
class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), default='Super Admin')
    email    = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    
    # ── FEEDBACK ──
class Feedback(db.Model):
    __tablename__ = 'feedbacks'
    id             = db.Column(db.Integer, primary_key=True)
    patient_id     = db.Column(db.Integer, db.ForeignKey('patients.id'))
    doctor_id      = db.Column(db.Integer, db.ForeignKey('doctors.id'))
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id'))
    rating         = db.Column(db.Integer, nullable=False)  # 1-5
    comment        = db.Column(db.Text)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)

# ── EMERGENCY CONTACT ──
class EmergencyContact(db.Model):
    __tablename__ = 'emergency_contacts'
    id           = db.Column(db.Integer, primary_key=True)
    patient_id   = db.Column(db.Integer, db.ForeignKey('patients.id'))
    name         = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(50))
    phone        = db.Column(db.String(15), nullable=False)
    email        = db.Column(db.String(100))