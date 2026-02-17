from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from config import Config
import threading
import time
import re
import os
import pickle
import numpy as np
import logging
from datetime import datetime

# Import Utils
from utils.risk_engine import calculate_risk_score
from utils.geo_lookup import get_geo_data
from utils.email_alert import send_alert_email
from utils.nlp_summary import generate_incident_summary
from model.shap_explainer import SOCExplainer

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

# ----------------------
# 🗄️ DATABASE MODELS
# ----------------------
class Alert(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    attack_type = db.Column(db.String(50), nullable=False)
    risk_score = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default="New") # New, Investigating, Resolved
    summary = db.Column(db.Text)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    country = db.Column(db.String(100))
    isp = db.Column(db.String(100))

# ----------------------
# 🧠 ML MODEL & GLOBALS
# ----------------------
soc_model = None
shap_explainer = None

def load_ml_components():
    global soc_model, shap_explainer
    try:
        model_path = os.path.join(app.config['BASE_DIR'], 'model', 'soc_model.pkl')
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                soc_model = pickle.load(f)
            print("✅ ML Model Loaded Successfully")
            
            # Initialize explainers (lazy load to save startup time if needed, but here we do it)
            # shap_explainer = SOCExplainer() # Uncomment if we fix the SHAP import
        else:
            print("⚠️ ML Model not found. Please run train_model.py")
    except Exception as e:
        print(f"❌ Error loading ML model: {e}")

# ----------------------
# 🔄 LOG INGESTION ENGINE
# ----------------------
def parse_log_line(line, log_type):
    """
    Parse a log line to extract features. 
    This is a simplified parser for our simulated logs.
    """
    # Regex patterns based on log_generator.py
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    timestamp_pattern = r'\[(.*?)\]'
    
    ip_match = re.search(ip_pattern, line)
    ip = ip_match.group(0) if ip_match else None
    
    timestamp_match = re.search(timestamp_pattern, line)
    timestamp = timestamp_match.group(1) if timestamp_match else datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not ip:
        return None

    # Feature Extraction (Simplified for mapped model)
    # Model expects: [failed_logins, packet_size, duration, port, is_internal]
    failed_logins = 0
    packet_size = 0
    duration = 0
    port = 0
    is_internal = 1 if ip.startswith("192.168") or ip.startswith("10.") else 0
    attack_label = "normal"
    
    if log_type == "auth":
        if "Failed login" in line:
            failed_logins = 5 # heuristic
            attack_label = "brute_force"
    elif log_type == "firewall":
        if "High traffic" in line:
            packet_size = 1000 # heuristic
            attack_label = "ddos"
    elif log_type == "network":
        if "Port scan" in line:
            port = 80 # default
            attack_label = "port_scan"
        elif "Suspicious outbound" in line:
            attack_label = "malware"
            
    return {
        "ip": ip,
        "timestamp": timestamp,
        "features": [failed_logins, packet_size, duration, port, is_internal],
        "attack_label_heuristic": attack_label,
        "raw_log": line
    }

def process_logs():
    """
    Background Task: Reads logs, extracts features, predicts with ML, and updates DB.
    """
    print("🕵️ Log Ingestion Engine Processing...")
    with app.app_context():
        # Ensure DB tables exist
        db.create_all()
        
        # Simple file pointer tracking (in memory for now, ideally persistent)
        log_files = {
            "auth": app.config['AUTH_LOG'],
            "network": app.config['NETWORK_LOG'],
            "firewall": app.config['FIREWALL_LOG']
        }
        
        files = {}
        for k, v in log_files.items():
            if os.path.exists(v):
                f = open(v, 'r')
                f.seek(0, 2) # Go to end
                files[k] = f
            else:
                print(f"⚠️ Log file not found: {v}")

        while True:
            for log_type, f in files.items():
                line = f.readline()
                if line:
                    data = parse_log_line(line, log_type)
                    if data and data['attack_label_heuristic'] != "normal":
                        # ML Prediction
                        prediction = "Unknown"
                        if soc_model:
                            try:
                                pred = soc_model.predict([data['features']])
                                prediction = pred[0]
                            except:
                                prediction = data['attack_label_heuristic']
                        else:
                            prediction = data['attack_label_heuristic']
                        
                        # Only alert on attacks
                        if prediction != "normal":
                             # Check if we already just alerted this IP to avoid spam
                            last_alert = Alert.query.filter_by(ip_address=data['ip']).order_by(Alert.id.desc()).first()
                            
                            # Simple dedup: if same IP and type within last 10s (simplified)
                            # For now, just log everything for visibility
                            
                            # Calculate Risk
                            risk = calculate_risk_score(prediction)
                            
                            # Geo Lookup
                            geo = get_geo_data(data['ip'])
                            
                            # NLP Summary
                            summary = generate_incident_summary(data['ip'], prediction, risk, data['timestamp'], data['raw_log'])
                            
                            # Save to DB
                            new_alert = Alert(
                                timestamp=data['timestamp'],
                                ip_address=data['ip'],
                                attack_type=prediction,
                                risk_score=risk,
                                summary=summary,
                                lat=geo['lat'],
                                lon=geo['lon'],
                                country=geo['country'],
                                isp=geo['isp']
                            )
                            db.session.add(new_alert)
                            db.session.commit()
                            
                            print(f"🚨 ALERT DETECTED: {prediction} from {data['ip']} (Risk: {risk})")
                            
                            # Email Alert
                            if risk > app.config['RISK_THRESHOLD']:
                                send_alert_email(
                                    "admin@example.com", 
                                    f"🚨 Critical SOC Alert: {prediction}", 
                                    summary, 
                                    app.config
                                )
                                
            # Sleep briefly
            time.sleep(1)

def start_background_thread():
    thread = threading.Thread(target=process_logs)
    thread.daemon = True
    thread.start()

# ----------------------
# 🌐 ROUTES
# ----------------------
@app.route('/')
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    # Metrics
    total_alerts = Alert.query.count()
    critical_alerts = Alert.query.filter(Alert.risk_score > 85).count()
    recent_alerts = Alert.query.order_by(Alert.id.desc()).limit(10).all()
    
    return render_template('dashboard.html', 
                           total_alerts=total_alerts, 
                           critical_alerts=critical_alerts,
                           recent_alerts=recent_alerts)

@app.route('/api/alerts')
def api_alerts():
    # Return recent alerts for JS polling
    alerts = Alert.query.order_by(Alert.id.desc()).limit(20).all()
    data = []
    for a in alerts:
        data.append({
            "id": a.id,
            "timestamp": a.timestamp,
            "ip": a.ip_address,
            "type": a.attack_type,
            "risk": a.risk_score,
            "country": a.country
        })
    return jsonify(data)

@app.route('/api/stats')
def api_stats():
    # Data for charts
    alerts = Alert.query.all()
    
    # Attack Types
    types = {}
    for a in alerts:
        types[a.attack_type] = types.get(a.attack_type, 0) + 1
        
    return jsonify({
        "attack_types": types,
        "total": len(alerts),
        "critical": sum(1 for a in alerts if a.risk_score > 85)
    })

@app.route('/map')
def map_view():
    alerts = Alert.query.all()
    # Filter only those with valid lat/lon
    map_data = [
        {"lat": a.lat, "lon": a.lon, "ip": a.ip_address, "risk": a.risk_score} 
        for a in alerts if a.lat and a.lon
    ]
    return render_template('map.html', map_data=map_data)

@app.route('/alerts')
def alerts_page():
    all_alerts = Alert.query.order_by(Alert.id.desc()).all()
    return render_template('alerts.html', alerts=all_alerts)

@app.route('/incident/<int:alert_id>')
def incident_details(alert_id):
    alert = Alert.query.get_or_404(alert_id)
    
    # Generate SHAP if needed (lazy) - For now just pass the alert
    # In a real app we'd call shap_explainer.generate_explanation(...) here and pass the image URL
    
    return render_template('incident.html', alert=alert)

@app.route('/analytics')
def analytics():
    return render_template('analytics.html')

@app.route('/settings')
def settings():
    return render_template('settings.html')

# ----------------------
# 🚀 ENTRY POINT
# ----------------------
if __name__ == '__main__':
    load_ml_components()
    
    # Use Flask's CLI or just run with python app.py
    # We start the background thread here, but be careful with reloader
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        start_background_thread()
        
    app.run(debug=True, host='0.0.0.0', port=5000)
