import requests
import sqlite3
import os

CACHE_FILE = "geo_cache.db" # Simple file-based cache or we can rely on main DB
# For simplicity in this structure, we'll hit the API and handle basic caching in memory or rely on the main DB later.
# But per instructions "Store latitude & longitude in database", we will return the data to be stored.

def get_geo_data(ip):
    """
    Fetch Geolocation data for a given IP.
    Returns a dictionary with lat, lon, country, city, isp.
    """
    # Filter generic local IPs
    if ip.startswith("192.168.") or ip.startswith("10.") or ip.startswith("127."):
        return {
            "lat": 0.0,
            "lon": 0.0,
            "country": "Local Network",
            "city": "Internal",
            "isp": "Private"
        }

    try:
        url = f"http://ip-api.com/json/{ip}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get("status") == "success":
            return {
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "country": data.get("country"),
                "city": data.get("city"),
                "isp": data.get("isp")
            }
    except Exception as e:
        print(f"Error fetching GeoIP for {ip}: {e}")
    
    return {
        "lat": 0.0,
        "lon": 0.0,
        "country": "Unknown",
        "city": "Unknown",
        "isp": "Unknown"
    }
