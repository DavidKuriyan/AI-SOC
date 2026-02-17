def generate_incident_summary(ip, attack_type, risk_score, timestamp, details=""):
    """
    Generate a human-readable summary of the incident.
    """
    
    severity = "Low"
    if risk_score > 85:
        severity = "CRITICAL"
    elif risk_score > 60:
        severity = "High"
    elif risk_score > 40:
        severity = "Medium"
        
    summary = (
        f"At {timestamp}, a {severity} severity security incident was detected from Source IP: {ip}. "
        f"The system identified the activity as '{attack_type}'. "
        f"Calculated Risk Score is {risk_score}/100. "
    )
    
    if "C2" in details:
        summary += "The host appears to be attempting to communicate with a known Command & Control server. Immediate isolation recommended."
    elif attack_type == "brute_force":
        summary += "Multiple failed login attempts detected, indicating a possible brute-force attack."
    elif attack_type == "ddos":
        summary += "Abnormally high traffic volume detected, characteristic of a Denial of Service attempt."
    elif attack_type == "port_scan":
        summary += "The source IP is sequentially scanning open ports on the network."
        
    return summary
