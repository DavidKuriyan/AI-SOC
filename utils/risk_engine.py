from datetime import datetime

def calculate_risk_score(attack_type, ip_history_count=0):
    """
    Calculate risk score based on attack type, time of day, and history.
    
    Attack Base Risk:
    - brute_force: 60
    - ddos: 80
    - malware: 90
    
    Modifiers:
    - After Midnight (00:00 - 06:00): +10
    - Repeated IP (history count > 5): +15
    """
    
    base_scores = {
        "brute_force": 60,
        "ddos": 80,
        "malware": 90,
        "port_scan": 40, # Added for completeness based on logs
        "suspicious_activity": 50
    }
    
    score = base_scores.get(attack_type, 30) # Default to 30 for unknown
    
    # Time Modifier: Check if current time is between 00:00 and 06:00
    current_hour = datetime.now().hour
    if 0 <= current_hour < 6:
        score += 10
        
    # Repetition Modifier
    if ip_history_count > 5:
        score += 15
        
    # Cap at 100
    return min(100, score)
