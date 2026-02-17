🛡️ AI-Based SOC Web Application
Full Stack + Machine Learning + Real-Time Monitoring + Explainable AI + NLP + Geo Mapping
💯 100% Free & Open-Source Tools
📌 Project Overview

The AI-Based Security Operations Center (SOC) Web Application is a full-stack cybersecurity monitoring platform that simulates enterprise-level attack detection using:

🔍 Machine Learning-based threat detection

📊 Real-time alert dashboard

🌍 IP Geolocation attack mapping

📩 Automated email alerts

🧠 Explainable AI (SHAP)

🤖 NLP-generated incident summaries

This project is designed as a final-year distinction-level cybersecurity + AI capstone project.

🚀 Key Features
🔐 1. Log Simulation (SOC Environment)

Simulated attack logs:

Failed Login (Brute Force)

Port Scanning

DDoS Attacks

Malware Communication

Logs stored in:

logs/
 ├── firewall.log
 ├── auth.log
 └── network.log

🧠 2. Machine Learning Detection

Trained using datasets like:

CICIDS 2017

UNSW-NB15

Model exported as:

model/soc_model.pkl


Prediction pipeline:

model = pickle.load(open("model/soc_model.pkl","rb"))
prediction = model.predict([features])

📊 3. Risk Scoring Engine

Custom SOC logic:

Attack Type	Base Risk
Brute Force	60
DDoS	80
Malware	90

Modifiers:

After Midnight → +10

Repeated IP → +15

Final:

risk_score = min(100, calculated_value)

🔄 4. Real-Time Dashboard (Auto Refresh)

API:

/api/alerts


Frontend refresh every 5 seconds:

setInterval(() => {
   fetch('/api/alerts')
   .then(res => res.json())
   .then(updateDashboard);
}, 5000);

🌍 5. IP Geolocation Mapping

Uses free IP API (ip-api.com)

Map rendered using Leaflet

Attack markers:

🔴 Critical

🟡 Medium

🟢 Low

📩 6. Email Alert System

Triggered when:

risk_score > 85


Uses:

Python smtplib

Gmail App Password

Example Email:

Subject: 🚨 Critical SOC Alert
Body:
Attack Type
IP Address
Risk Score
Incident Summary

🧠 7. Explainable AI (SHAP)

Install:

pip install shap


Features:

Feature contribution visualization

Top 5 risk factors

SHAP summary plots

Model transparency

Saved and displayed in Incident Details page.

🤖 8. NLP-Based Incident Summary

Basic:

def generate_summary(ip, attack, risk):
    return f"Suspicious {attack} detected from {ip} with risk score {risk}."


Advanced (Optional):

Transformer-based summarizer

🌐 Web Application Structure
🔐 Login Page

Route:

/login

📊 Dashboard

Route:

/dashboard


Displays:

Total Alerts

Critical Alerts

Risk Gauge

Attack Distribution Chart

Real-Time Alert Table

🚨 Alerts Page

Route:

/alerts


| Time | IP | Type | Risk | Status |

Filter by:

Low

Medium

High

Critical

📁 Incident Details

Route:

/incident/<id>


Displays:

Raw log

ML prediction

Risk breakdown

SHAP explanation

Geo Map location

NLP summary

Block IP button

🌍 Geo Map

Route:

/map


World map with attack markers.

📈 Analytics

Route:

/analytics


Charts:

Attack trends

Top IPs

Risk distribution

Daily attack count

⚙️ Settings

Route:

/settings


Options:

Change risk threshold

Add trusted IP

Clear logs

🏗️ Project Structure
ai-soc-automation/
│
├── app.py
├── config.py
│
├── model/
│   ├── train_model.py
│   ├── soc_model.pkl
│   ├── shap_explainer.py
│
├── logs/
│
├── database/
│   ├── soc.db
│
├── utils/
│   ├── risk_engine.py
│   ├── geo_lookup.py
│   ├── email_alert.py
│   ├── nlp_summary.py
│
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── alerts.html
│   ├── incident.html
│   ├── map.html
│   ├── analytics.html
│   ├── settings.html
│
├── static/
│   ├── css/
│   ├── js/
│
└── requirements.txt

📊 Performance Metrics (For Report)

Include:

Accuracy

Precision

Recall

F1-Score

Confusion Matrix

ROC Curve

Explain:

False Positive: Benign activity detected as attack
False Negative: Real attack not detected

🎨 UI/UX Design

Theme:

Background: #121212

Neon Green: #00FF9F

Critical Red: #FF3B3B

Layout:

Top Navbar
Left Sidebar
Main Content Panel


Professional SOC-style dashboard appearance.

🛠️ Installation & Run Guide

### Option 1: Easy Start (Windows)
Double-click `run_soc.bat` in the project root. This will launch both the simulator and the dashboard automatically.

### Option 2: Manual Setup

1️⃣ **Clone Repository**
```bash
git clone https://github.com/DavidKuriyan/AI-SOC.git
cd AI-SOC/ai-soc-automation
```

2️⃣ **Install Dependencies**
```bash
pip install -r requirements.txt
```

3️⃣ **Run Log Simulator (Terminal 1)**
```bash
python log_generator.py
```

4️⃣ **Run Web Dashboard (Terminal 2)**
```bash
python app.py
```

5️⃣ **Access Dashboard**
Open: http://127.0.0.1:5000

📚 Technologies Used

Python (Flask)

SQLite

Scikit-learn

SHAP

Leaflet.js

JavaScript

HTML/CSS

SMTP (Email)

All tools are 100% free and open-source.

🎓 Project Level Evaluation
Feature	Level
Basic SOC	6/10
+ ML	7.5/10
+ Real-Time	8/10
+ Geo Map	8.5/10
+ Email	9/10
+ SHAP	9.3/10
+ NLP	9.5/10

🔥 Near industry-level SOC prototype.

👨‍💻 Author

David Kuriyan