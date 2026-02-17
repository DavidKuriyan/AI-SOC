import pandas as pd
import numpy as np
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import os

# Create model directory
MODEL_DIR = "model"
os.makedirs(MODEL_DIR, exist_ok=True)
MODEL_PATH = os.path.join(MODEL_DIR, "soc_model.pkl")

def train_soc_model():
    print("🧠 Starting Model Training...")
    
    # Simulate a dataset (since we don't have the full CSVs available efficiently)
    # Features: [failed_logins, packet_size, duration, port, is_internal_ip]
    # is_internal_ip: 1 = yes, 0 = no
    
    # Generate Synthetic Data
    n_samples = 1000
    
    data = []
    labels = []
    
    for _ in range(n_samples):
        # Normal Traffic
        if os.urandom(1)[0] % 2 == 0:
            failed_logins = np.random.randint(0, 2)
            packet_size = np.random.randint(50, 1500)
            duration = np.random.randint(1, 60)
            port = np.random.choice([80, 443, 53])
            is_internal = 1
            label = "normal"
            
        else:
            attack_type = np.random.choice(["brute_force", "ddos", "port_scan", "malware"])
            
            if attack_type == "brute_force":
                failed_logins = np.random.randint(5, 50)
                packet_size = np.random.randint(100, 500)
                duration = np.random.randint(10, 300)
                port = 22
                is_internal = 0
                label = "brute_force"
                
            elif attack_type == "ddos":
                failed_logins = 0
                packet_size = np.random.randint(64, 128) # Small packets usually
                duration = np.random.randint(1, 5) # Short bursts
                port = 80
                is_internal = 0
                label = "ddos"
                
            elif attack_type == "port_scan":
                failed_logins = 0
                packet_size = 64
                duration = 1
                port = np.random.randint(1, 65535)
                is_internal = 0
                label = "port_scan"
                
            elif attack_type == "malware":
                failed_logins = 0
                packet_size = np.random.randint(2000, 5000) # Exfiltration
                duration = np.random.randint(100, 1000)
                port = np.random.choice([4444, 6667, 8080])
                is_internal = 1 # Compromised host
                label = "malware"

        data.append([failed_logins, packet_size, duration, port, is_internal])
        labels.append(label)

    X = np.array(data)
    y = np.array(labels)

    # Train Logic
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X_train, y_train)
    
    # Evaluation
    print("✅ Model Trained!")
    print("📊 Classification Report:")
    y_pred = clf.predict(X_test)
    print(classification_report(y_test, y_pred))
    
    # Save Model
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(clf, f)
        
    print(f"💾 Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train_soc_model()
