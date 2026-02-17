import time
import random
import logging
import os
from datetime import datetime

# Setup log directories
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Setup independent loggers
def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('%(message)s')
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

auth_logger = setup_logger('auth', os.path.join(LOG_DIR, 'auth.log'))
network_logger = setup_logger('network', os.path.join(LOG_DIR, 'network.log'))
firewall_logger = setup_logger('firewall', os.path.join(LOG_DIR, 'firewall.log'))

# Simulation Data
IPS = [
    "192.168.1.10", "10.0.0.5", "172.16.0.22",  # Local/Safe
    "103.45.22.1", "45.33.21.9", "67.22.90.5", "185.220.101.9",  # Malicious/External
    "192.168.1.15", "192.168.1.20"
]

USERS = ["admin", "root", "user1", "guest", "test_user"]
PORTS = [22, 80, 443, 3306, 8080, 21]

def generate_log():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ip = random.choice(IPS)
    
    # 1. Failed Login (Brute Force)
    if random.random() < 0.3:
        user = random.choice(USERS)
        log_entry = f"[{timestamp}] [AUTH] Failed login for user '{user}' from {ip}"
        auth_logger.info(log_entry)
        print(f"Generated: {log_entry}")

    # 2. Port Scanning
    if random.random() < 0.2:
        port = random.choice(PORTS)
        log_entry = f"[{timestamp}] [NETWORK] Port scan detected on port {port} from {ip}"
        network_logger.info(log_entry)
        print(f"Generated: {log_entry}")

    # 3. DDoS / High Traffic
    if random.random() < 0.15:
        log_entry = f"[{timestamp}] [FIREWALL] High traffic detected: {random.randint(500, 5000)} packets/sec from {ip}"
        firewall_logger.info(log_entry)
        print(f"Generated: {log_entry}")
        
    # 4. Malware Communication
    if random.random() < 0.1:
        dest_ip = f"185.100.{random.randint(1,255)}.{random.randint(1,255)}"
        log_entry = f"[{timestamp}] [NETWORK] Suspicious outbound connection to C2 server {dest_ip} from {ip}"
        network_logger.info(log_entry)
        print(f"Generated: {log_entry}")

    # 5. Normal Traffic (Noise)
    if random.random() < 0.4:
         log_entry = f"[{timestamp}] [INFO] Authorized access from 192.168.1.{random.randint(2, 50)}"
         auth_logger.info(log_entry)

if __name__ == "__main__":
    print("🚀 Starting SOC Log Simulator... Logs will be written to ai-soc-automation/logs/")
    try:
        while True:
            generate_log()
            time.sleep(random.uniform(0.5, 3.0)) # Random delay between 0.5 and 3 seconds
    except KeyboardInterrupt:
        print("\n⏹️ Log Simulator Stopped.")
