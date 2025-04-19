# 🌡️ Docify - Smart Heart Disease Prediction Web App

**Docify** is a full-stack web application built with Flask that predicts heart disease risk using a machine learning model. It includes secure authentication, role-based dashboards for patients and doctors, medical report uploads, and real-time prediction with probability and risk levels.

## 🚀 Features

- 🔐 **User Authentication** (Signup / Signin)
- 🩺 **Role-Based Access** (Patient & Doctor)
- 📄 **Medical Report Uploads** and Viewing
- 🧠 **ML-Based Prediction** of Heart Disease Risk
- 📊 **Risk Level & Probability Display**
- 👨‍⚕️ **Doctor Recommendation System** (based on risk level)
- 🗂️ **User-Friendly Dashboards** for patients and doctors

## 🛠️ Tech Stack

| Frontend      | Backend      | Machine Learning | Database | Others       |
|---------------|--------------|------------------|----------|--------------|
| HTML, CSS, JS | Flask (Python) | RandomForest / XGBoost | SQLite   | sessionStorage, API integration |

## 📸 Screenshots

_Add screenshots here if available:_
- Landing Page
- Prediction Result Page
- Patient Dashboard
- Doctor Dashboard

## 🧪 Prediction Flow

1. User logs in as patient or doctor.
2. Patient fills out a medical form.
3. Data is preprocessed and passed to an ML model.
4. App displays:
   - Prediction (Positive/Negative)
   - Risk Level (Low / Medium / High)
   - Probability Score
5. Doctor recommendations appear if needed.

## 📂 Folder Structure
Docify/ ├── static/ ├── templates/ ├── model/ │ └── model.pkl ├── disease/ │ └── heart.csv ├── train_model.py ├── app.py ├── requirements.txt └── README.md


## 🧰 How to Run Locally

```bash
# Clone the repository
git clone https://github.com/Isupersatan/Docify.git
cd Docify

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

💡 Future Enhancements
✅ Add unit and integration tests

📤 Deploy on Render / Vercel / Heroku

📧 Email alerts for high-risk predictions

🌈 Improved UI with Tailwind or Bootstrap

🧠 ML Model Details
Preprocessing: Binning, One-Hot Encoding

Algorithm: RandomForestClassifier / XGBoost

Evaluation Metrics: Accuracy, Precision, Probability Score

Custom risk level logic based on prediction confidence

👨‍💻 Author
Sayan – @Isupersatan

MCA Student | Full-Stack Developer | Machine Learning Enthusiast


---

Let me know if you'd like a version with markdown styling for GitHub badges or deployment steps (like for Render/Heroku).
