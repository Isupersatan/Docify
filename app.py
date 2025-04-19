import datetime
import pandas as pd

from flask import Flask, render_template, request, redirect, session, flash, url_for,request,send_from_directory,jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import os
from werkzeug.utils import secure_filename
from datetime import datetime




app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@localhost/docify'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'signin'

class User(db.Model, UserMixin):
    email = db.Column(db.String(50), primary_key=True)  # Increase length for email
    name = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(200), nullable=False)  # Increase length for hashed passwords
    gender = db.Column(db.String(10), nullable=False)
    u_type = db.Column(db.String(10), nullable=False)
    b_date = db.Column(db.String(12), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
        print(f"Debug: Hashed password = {self.password}")  # Debugging



    def check_password(self, password):
        print(f"Debug: Comparing plaintext password = {password} with hashed password = {self.password}")  # Debugging
        is_correct = check_password_hash(self.password, password)
        print(f"Debug: Password comparison result = {is_correct}")  # Debugging
        return is_correct

    def get_id(self):
        return self.email

@login_manager.user_loader
def load_user(email):
    print(f"Debug: Loading user with email = {email}")  # Debugging
    return User.query.get(email)

class PatientDetails(db.Model):
    p_id = db.Column(db.Integer, primary_key=True)
    p_email = db.Column(db.String(50), db.ForeignKey('user.email'), nullable=False)
    p_name = db.Column(db.String(50), nullable=False)
    p_dob = db.Column(db.String(12), nullable=False)
    p_age = db.Column(db.Integer)
    weight = db.Column(db.Float)
    height = db.Column(db.Float)
    report_path = db.Column(db.String(255))
    report_filename = db.Column(db.String(255))

class DoctorDetails(db.Model):
    d_id = db.Column(db.Integer, primary_key=True)
    d_email = db.Column(db.String(50), db.ForeignKey('user.email'), nullable=False)
    d_name = db.Column(db.String(50), nullable=False)
    d_dob = db.Column(db.String(12), nullable=False)
    d_age = db.Column(db.Integer)
    specialist = db.Column(db.String(50))
    rating = db.Column(db.Float)
    license_path = db.Column(db.String(255))
    photo_path = db.Column(db.String(255))

@app.route("/")
def theme():
    return render_template('theme.html', redirect_url='index', timeout=2000)

@app.route("/index")
def index():
    return render_template('index.html')

#from models import DoctorDetails, PatientDetails  # import if needed

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            email = request.form.get('email')
            password = request.form.get('password')
            gender = request.form.get('gender')
            u_type = request.form.get('role')
            b_date = request.form.get('DOB')

            user = User(name=name, email=email, gender=gender, u_type=u_type, b_date=b_date)
            user.set_password(password)  # Hash the password
            db.session.add(user)
            db.session.flush()  # Flush to assign ID if needed

            # Insert into doctor_details or patient_details based on role
            if u_type.lower() == 'doctor':
                doctor = DoctorDetails(
                    d_email=email,
                    d_name=name,
                    d_dob=b_date,
                    d_age=0,  # You can calculate age if needed
                    specialist="Not specified",  # Default or fetched from form
                    rating=0.0,
                    license_path="",  # Handle this from form if needed
                    photo_path=""
                )
                db.session.add(doctor)

            elif u_type.lower() == 'patient':
                patient = PatientDetails(
                    p_email=email,
                    p_name=name,
                    p_dob=b_date,
                    p_age=0,  # Same as above
                    weight=0.0,
                    height=0.0,
                    report_path="",
                    report_filename=""
                )
                db.session.add(patient)

            db.session.commit()
            flash('Signup successful!', 'success')
            return redirect('signin')

        except Exception as e:
            db.session.rollback()
            print("ERROR during signup:", str(e))
            flash(f'An error occurred: {str(e)}', 'error')

    return render_template("signup.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        role = request.form['role'].lower().strip()
        email = request.form['email'].strip()
        password = request.form['password']
        print(f"Debug: Role = {role}, Email = {email}, Password = {password}")  # Debugging

        # Dummy admin credentials
        if role == 'admin' and email == 'admin@gmail.com' and password == 'admin123':
            session['user'] = email
            session['role'] = role
            session['admin'] = {
                'id': 2,
                'name': 'Mr. Rahul',
                'email': 'admin@gmail.com'
            }
            return redirect(url_for('admin'))  # Redirect to admin.html

        # SQL check (for debugging)
        query = text("SELECT * FROM user WHERE email = :email AND u_type = :u_type")
        result = db.session.execute(query, {"email": email, "u_type": role}).fetchone()
        print(f"Debug: Raw SQL result = {result}")  # Debugging

        # Query user from ORM
        user = User.query.filter_by(email=email, u_type=role).first()
        print(f"Debug: User found = {user}")  # Debugging

        if user:
            print(f"Debug: User password hash = {user.password}")  # Debugging
            if user.check_password(password):
                print("Debug: Password is correct")  # Debugging
                login_user(user)
                print(f"Debug: Current user = {current_user}")  # Debugging
                flash('Login successful!', 'success')

                # Redirect based on role
                if user.u_type == 'doctor':
                    return redirect(url_for('doctor'))
                elif user.u_type == 'patient':
                    return redirect(url_for('patient'))
            else:
                print("Debug: Invalid password")  # Debugging
                flash('Invalid password', 'error')
        else:
            print("Debug: User not found")  # Debugging
            flash('Invalid email or role', 'error')

    return render_template('signin.html')


@app.route('/admin')
def admin():
    return render_template('admin.html',admin_page=True)







@app.route("/patient", methods=['GET', 'POST'])
@login_required
def patient():
    if current_user.u_type.lower() != 'patient':  # Case-insensitive comparison
        flash('You do not have access to this page.', 'error')
        return redirect(url_for('signin'))

    patient_details = PatientDetails.query.filter_by(p_email=current_user.email).first()

    if not patient_details:
        patient_details = PatientDetails(
            p_email=current_user.email,
            p_name=current_user.name,
            p_dob=current_user.b_date,
            p_age=25,  # Default age (adjust as needed)
            weight=70.0,  # Default weight
            height=170.0,  # Default height
            report_path=""
        )
        db.session.add(patient_details)
        db.session.commit()

    return render_template('patient.html', patient=patient_details )

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/update_patient', methods=['POST'])
@login_required
def update_patient():
    if current_user.u_type.lower() != 'patient':
        flash('Access denied', 'error')
        return redirect(url_for('signin'))

    try:
        # Get form data
        p_name = request.form.get('p_name')
        p_age = request.form.get('p_age')
        p_dob = request.form.get('p_dob')
        height = request.form.get('height')
        weight = request.form.get('weight')
        p_email = request.form.get('p_email')  # From hidden field

        # Find existing patient or create new
        patient = PatientDetails.query.filter_by(p_email=p_email).first()

        if not patient:
            patient = PatientDetails(p_email=p_email)
            db.session.add(patient)

        # Update patient details
        patient.p_name = p_name
        patient.p_age = p_age
        patient.p_dob = p_dob
        patient.height = float(height)
        patient.weight = float(weight)

        # Handle file upload
        if 'medical_report' in request.files:
            file = request.files['medical_report']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Create uploads folder if it doesn't exist
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)

                # Update patient record with file info
                patient.report_path = filepath
                patient.report_filename = filename

        db.session.commit()
        flash('Profile updated successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error updating profile: {str(e)}', 'error')

    return redirect(url_for('patient'))


@app.route('/view_report/<patient_email>')
@login_required
def view_report(patient_email):
    if current_user.u_type.lower() != 'patient' or current_user.email != patient_email:
        flash('Access denied', 'error')
        return redirect(url_for('signin'))

    patient = PatientDetails.query.filter_by(p_email=patient_email).first()
    if not patient or not patient.report_path:
        flash('No medical report found', 'error')
        return redirect(url_for('patient'))

    return send_from_directory(
        os.path.dirname(patient.report_path),
        os.path.basename(patient.report_path),
        as_attachment=False
    )


@app.route('/doctor', methods=['GET', 'POST'])
@login_required
def doctor():
    if current_user.u_type.lower() != 'doctor':
        flash('Access denied', 'error')
        return redirect(url_for('signin'))

    # Proper boolean handling from query params
    booked = request.args.get('booked', 'false').lower() == 'true'
    patient_email = request.args.get('patient_email')

    # Enhanced debug prints
    print(f"DEBUG - Booked: {booked} (type: {type(booked)}), Patient Email: {patient_email}")

    doctor = DoctorDetails.query.filter_by(d_email=current_user.email).first()

    patient = None
    if booked and patient_email:
        patient = PatientDetails.query.filter_by(p_email=patient_email).first()
        print(f"DEBUG - Patient found: {patient is not None}, Email: {patient_email}")

    return render_template('doctor.html',
                         doctor=doctor,
                         patient=patient,
                         booked=booked)


@app.route('/update_doctor', methods=['POST'])
@login_required
def update_doctor():
    if current_user.u_type.lower() != 'doctor':
        flash('Access denied', 'error')
        return redirect(url_for('signin'))

    try:
        d_name = request.form.get('d_name')
        d_age = request.form.get('d_age')
        d_dob = request.form.get('d_dob')
        specialist = request.form.get('specialist')
        d_email = request.form.get('d_email')

        doctor = DoctorDetails.query.filter_by(d_email=d_email).first()

        if not doctor:
            doctor = DoctorDetails(d_email=d_email)
            db.session.add(doctor)

        doctor.d_name = d_name
        doctor.d_age = d_age
        doctor.d_dob = d_dob
        doctor.specialist = specialist

        # Uploads
        if 'license_file' in request.files:
            file = request.files['license_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                doctor.license_path = filepath

        if 'photo_file' in request.files:
            file = request.files['photo_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                doctor.photo_path = filepath

        db.session.commit()
        flash('Doctor profile updated successfully!', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Error updating profile: {str(e)}', 'error')

    return redirect(url_for('doctor'))



@app.route('/view_license/<doctor_email>')
@login_required
def view_license(doctor_email):
    if current_user.u_type.lower() != 'doctor' or current_user.email != doctor_email:
        flash('Access denied', 'error')
        return redirect(url_for('signin'))

    doctor = DoctorDetails.query.filter_by(d_email=doctor_email).first()
    if not doctor or not doctor.license_path:
        flash('License file not found', 'error')
        return redirect(url_for('doctor'))

    return send_from_directory(
        os.path.dirname(doctor.license_path),
        os.path.basename(doctor.license_path),
        as_attachment=False
    )


@app.route('/view_photo/<doctor_email>')
@login_required
def view_photo(doctor_email):
    if current_user.u_type.lower() != 'doctor' or current_user.email != doctor_email:
        flash('Access denied', 'error')
        return redirect(url_for('signin'))

    doctor = DoctorDetails.query.filter_by(d_email=doctor_email).first()
    if not doctor or not doctor.photo_path:
        flash('Photo not found', 'error')
        return redirect(url_for('doctor'))

    return send_from_directory(
        os.path.dirname(doctor.photo_path),
        os.path.basename(doctor.photo_path),
        as_attachment=False
    )


@app.route('/api/doctors')
def get_cardiologists():
    specialty = request.args.get('specialist', 'Heart')  # ✅ FIXED


    doctors = DoctorDetails.query.filter(DoctorDetails.specialist.ilike(f"%{specialty}%")).all()

    doctor_list = [
        {
            'd_id': doc.d_id,
            'd_name': doc.d_name,
            'specialist': doc.specialist,
            'd_email': doc.d_email
        }
        for doc in doctors
    ]

    return jsonify(doctor_list)





@app.route("/login")
def login():
    return render_template('login.html')


from flask_wtf.csrf import generate_csrf


@app.route('/heart')
@login_required
def heart():
    return render_template('heart.html')

# Load heart disease prediction model and scaler
try:
    import pickle
    with open("model/heart_model.pkl", "rb") as f:
        heart_model = pickle.load(f)
    with open("model/scaler.pkl", "rb") as f:
        heart_scaler = pickle.load(f)
    print("✅ Random Forest model and scaler loaded successfully")
except Exception as e:
    print(f"❌ Error loading model or scaler: {str(e)}")
    heart_model = None
    heart_scaler = None


@app.route('/predict', methods=['POST'])
@login_required
def predict():
    try:
        # Get input data (handles both JSON and form data)
        data = request.get_json() if request.is_json else request.form
        current_user_id = current_user.get_id()

        print("📥 Received prediction request from user:", current_user_id)
        print("📦 Raw input data:", data)

        # Validate required fields
        required_fields = [
            'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg',
            'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'
        ]

        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            error_msg = f'Missing required fields: {", ".join(missing_fields)}'
            print("❌ Validation error:", error_msg)
            return jsonify({'error': error_msg}), 400

        # Convert and validate numeric fields
        try:
            input_data = {
                'age': float(data['age']),
                'sex': int(data['sex']),
                'cp': int(data['cp']),
                'trestbps': float(data['trestbps']),
                'chol': float(data['chol']),
                'fbs': int(data['fbs']),
                'restecg': int(data['restecg']),
                'thalach': float(data['thalach']),
                'exang': int(data['exang']),
                'oldpeak': float(data['oldpeak']),
                'slope': int(data['slope']),
                'ca': int(data['ca']),
                'thal': int(data['thal'])
            }
        except ValueError as e:
            print("❌ Type conversion error:", str(e))
            return jsonify({'error': f'Invalid input value: {str(e)}'}), 400

        # Validate value ranges
        validation_errors = []
        if not (20 <= input_data['age'] <= 120):
            validation_errors.append("Age must be between 20-120")
        if not (80 <= input_data['trestbps'] <= 200):
            validation_errors.append("Resting blood pressure must be between 80-200 mmHg")
        if not (100 <= input_data['chol'] <= 600):
            validation_errors.append("Cholesterol must be between 100-600 mg/dL")
        if input_data['ca'] not in [0, 1, 2, 3]:
            validation_errors.append("Major vessels must be between 0-3")
        if input_data['thal'] not in [1, 2, 3]:
            validation_errors.append("Thalassemia must be 1, 2, or 3")

        if validation_errors:
            print("❌ Validation errors:", validation_errors)
            return jsonify({'error': " | ".join(validation_errors)}), 400

        # Create DataFrame with columns in same order as training
        input_df = pd.DataFrame([input_data], columns=required_fields)

        # Apply scaling
        scaled_input = heart_scaler.transform(input_df)

        # Make prediction
        prediction_proba = heart_model.predict_proba(scaled_input)[0][1]  # Probability of heart disease
        prediction_class = heart_model.predict(scaled_input)[0]

        # Determine risk level
        probability = float(round(prediction_proba * 100, 2))
        if probability >= 60:
            risk_level = 'High'
        elif probability >= 30:
            risk_level = 'Medium'
        else:
            risk_level = 'Low'

        # Prepare result data
        result = {
            'probability': probability,
            'risk_level': risk_level,
            'has_disease': bool(prediction_class),
            'message': f"Heart disease risk: {probability}% ({risk_level} risk)",
            'timestamp': datetime.now().isoformat()
        }

        # Store in session for the result pages
        session['heart_prediction'] = result

         # Log prediction for analytics (optional)
        # log_prediction(current_user_id, input_data, result)

        print(f"✅ Prediction complete - Risk: {risk_level} ({probability}%)")

        # Return JSON for AJAX or redirect for form submissions
        if request.is_json:
            return jsonify(result)
        else:
            if prediction_class:  # High risk
                return redirect(url_for('high_risk_result'))
            else:  # Low risk
                return redirect(url_for('low_risk_result'))

    except Exception as e:
        print("❌ Unexpected error during prediction:", str(e))
        error_msg = 'An unexpected error occurred during prediction'
        if request.is_json:
            return jsonify({'error': error_msg}), 500
        else:
            flash(error_msg, 'error')
            return redirect(url_for('heart'))


@app.route('/yes-ht-ds')
@login_required
def high_risk_result():
    prediction_data = session.get('heart_prediction')
    if not prediction_data:
        flash('No prediction data found', 'error')
        return redirect(url_for('heart'))

    patient = PatientDetails.query.filter_by(p_email=current_user.email).first()
    if not patient:
        flash('Please complete your patient profile first', 'warning')
        return redirect(url_for('patient'))

    context = {
        'probability': prediction_data.get('probability', 0),
        'risk_level': prediction_data.get('risk_level', 'High'),
        'message': prediction_data.get('message', ''),
        'patient': patient
    }

    print(f"DEBUG - Rendering high risk result for patient: {current_user.email}")
    return render_template('yes-ht-ds.html', **context)


@app.route('/no-ht-ds')
@login_required
def low_risk_result():
    prediction_data = session.get('heart_prediction')
    if not prediction_data:
        flash('No prediction data found', 'error')
        return redirect(url_for('heart'))
    patient = PatientDetails.query.filter_by(p_email=current_user.email).first()
    if not patient:
        flash('Please complete your patient profile first', 'warning')
        return redirect(url_for('patient'))

    context = {
        'probability': prediction_data.get('probability', 0),
        'risk_level': prediction_data.get('risk_level', 'High'),
        'message': prediction_data.get('message', ''),
        'patient': patient,
        'booked': request.args.get('booked', 'false') == 'true',
        'booked_doctor_email': request.args.get('doctor_email', None)
    }

    print(f"DEBUG - Rendering high risk result for patient: {current_user.email}")
    return render_template('no-ht-ds.html', **context)


@app.route('/book_appointment', methods=['POST'])
@login_required
def book_appointment():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400

        doctor_email = data.get('doctor_email')
        patient_email = current_user.email

        print(f"DEBUG - Booking attempt - Doctor: {doctor_email}, Patient: {patient_email}")

        doctor = DoctorDetails.query.filter_by(d_email=doctor_email).first()
        patient = PatientDetails.query.filter_by(p_email=patient_email).first()

        if not doctor:
            print("DEBUG - Doctor not found")
            return jsonify({'success': False, 'message': 'Doctor not found'}), 404
        if not patient:
            print("DEBUG - Patient not found")
            return jsonify({'success': False, 'message': 'Patient profile not complete'}), 404

        print("DEBUG - Preparing redirect URL")

        # ✅ Include doctor_name in response
        return jsonify({
            'success': True,
            'redirect_url': url_for('doctor',
                                    booked='true',
                                    patient_email=patient_email,
                                    _external=True),
            'message': 'Appointment booked successfully',
            'doctor_name': doctor.d_name  # <-- This ensures JS gets the name
        })

    except Exception as e:
        print(f"ERROR in book_appointment: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500



if __name__ == '__main__':
    with app.app_context():
        db.drop_all()  # Drop all tables (use with caution in production)
        db.create_all()  # Recreate all tables based on the current models
    app.run(debug=True)