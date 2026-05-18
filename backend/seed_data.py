from app import app
from models import db, Patient, Doctor, Department, Admin
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

    depts = [
        Department(name='Cardiology',  emoji='❤️'),
        Department(name='Orthopedic',  emoji='🦴'),
        Department(name='Neurology',   emoji='🧠'),
        Department(name='Eye Care',    emoji='👁️'),
        Department(name='Dental',      emoji='🦷'),
        Department(name='Pediatrics',  emoji='👶'),
        Department(name='Dermatology', emoji='🌿'),
        Department(name='General',     emoji='🩺'),
    ]
    for d in depts:
        if not Department.query.filter_by(name=d.name).first():
            db.session.add(d)
    db.session.commit()
    print("✅ Departments added")

    doctors_data = [
        ('Dr. Rajesh Sharma', 'rajesh@medicare.com', 'Cardiologist',      'Cardiology',  '12 years', 500),
        ('Dr. Anita Patel',   'anita@medicare.com',  'Neurologist',        'Neurology',   '9 years',  600),
        ('Dr. Manish Kumar',  'manish@medicare.com', 'Orthopedic Surgeon', 'Orthopedic',  '15 years', 550),
        ('Dr. Sunita Rao',    'sunita@medicare.com', 'Dermatologist',      'Dermatology', '7 years',  400),
        ('Dr. Vikram Singh',  'vikram@medicare.com', 'Eye Specialist',     'Eye Care',    '10 years', 450),
        ('Dr. Meera Iyer',    'meera@medicare.com',  'Dentist',            'Dental',      '8 years',  350),
        ('Dr. Arjun Nair',    'arjun@medicare.com',  'Pediatrician',       'Pediatrics',  '11 years', 400),
        ('Dr. Prerna Gupta',  'prerna@medicare.com', 'General Physician',  'General',     '6 years',  300),
    ]
    for name, email, spec, dept_name, exp, fee in doctors_data:
        if not Doctor.query.filter_by(email=email).first():
            dept = Department.query.filter_by(name=dept_name).first()
            doc  = Doctor(
                name=name, email=email,
                password=generate_password_hash('doctor123'),
                specialization=spec, department_id=dept.id,
                experience=exp, fee=fee, status='available'
            )
            db.session.add(doc)
    db.session.commit()
    print("✅ Doctors added")

    if not Admin.query.filter_by(email='admin@medicare.com').first():
        admin = Admin(name='Super Admin', email='admin@medicare.com',
                      password=generate_password_hash('admin123'))
        db.session.add(admin)
        db.session.commit()
    print("✅ Admin added")

    if not Patient.query.filter_by(email='rahul@email.com').first():
        patient = Patient(
            first_name='Rahul', last_name='Singh',
            email='rahul@email.com',
            password=generate_password_hash('patient123'),
            phone='+91 98765 43210', gender='Male',
            blood_group='B+', address='42 MG Road, Ludhiana'
        )
        db.session.add(patient)
        db.session.commit()
    print("✅ Test patient added")

    print("\n🎉 Database ready!")
    print("Patient → rahul@email.com    / patient123")
    print("Doctor  → rajesh@medicare.com / doctor123")
    print("Admin   → admin@medicare.com  / admin123")