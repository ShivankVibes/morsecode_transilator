# <-----FOR RUNNING THE PROJECT,PLEASE FOLLOW THE INSTRUCTIONS BELOW----->
# 1. Install the required dependencies using pip:
#    pip install requests
# 2. Replace the API_KEY variable with your actual Hackatime API key.
# 3. Run the script using Python:
#   FOR WINDOWS->  python fakebeat.py
#   FOR MAC/Linux-> python3 fakebeat.py
import time
import base64
import random
import requests
import os

# --- HACKATIME CONFIGURATION ---
API_KEY = '9c71f275-ff73-4998-803f-7276c88ef1e4'

# Realistic human project arrays mapped directly to calendar days
DAILY_PROJECTS = {
    "Monday":    {"project": "personal-portfolio", "files": [("index.html", "HTML"), ("style.css", "CSS"), ("script.js", "JavaScript")]},
    "Tuesday":   {"project": "discord-moderator-bot", "files": [("bot.py", "Python"), ("config.json", "JSON"), ("utils.py", "Python")]},
    "Wednesday": {"project": "react-ecommerce-dashboard", "files": [("App.jsx", "JavaScript"), ("Navbar.jsx", "JavaScript"), ("theme.ts", "TypeScript")]},
    "Thursday":  {"project": "algorithm-practice", "files": [("binary_search.py", "Python"), ("sorting.js", "JavaScript")]},
    "Friday":    {"project": "rest-api-backend", "files": [("server.js", "JavaScript"), ("routes.go", "Go"), ("models.py", "Python")]},
    "Saturday":  {"project": "game-dev-testing", "files": [("player_movement.cs", "C#"), ("enemy_ai.py", "Python")]},
    "Sunday":    {"project": "open-source-contributions", "files": [("README.md", "Markdown"), ("bug_fix.py", "Python")]}
}
# -------------------------------

def encode_api_key(key):
    encoded = base64.b64encode(key.encode('utf-8')).decode('utf-8')
    return f"Basic {encoded}"

def send_heartbeat():
    # FIXED URL: Locked down to the correct path
    url = "https://hackatime.hackclub.com/api/hackatime/v1/users/current/heartbeats"
    
    headers = {
        "Authorization": encode_api_key(API_KEY),
        "Content-Type": "application/json"
    }
    
    # 1. Dynamically find current real-world day name based on system clock
    current_day = time.strftime("%A")
    workspace = DAILY_PROJECTS[current_day]
    
    project_name = workspace["project"]
    # 2. Pick a random file from that project profile to simulate tab-switching
    file_name, language = random.choice(workspace["files"])
    
    mock_path = os.path.join("Projects", project_name, file_name)
    
    payload = [{
        "entity": mock_path,
        "type": "file",
        "language": language,
        "project": project_name,
        "branch": "main",
        "is_write": random.choice([True, False]), # Simulates typing variations vs saving files
        "lines": random.randint(45, 310),
        "time": time.time()
    }]
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if 200 <= response.status_code < 300:
            print(f"[+] Synced: Active on '{project_name}' -> Working inside '{file_name}' ({time.strftime('%X')})")
        else:
            print(f"[-] Dropped by server. Status code: {response.status_code}")
    except Exception as e:
        print(f"[-] Script transmission error: {e}")

if __name__ == "__main__":
    print("[*] Starting Humanized Calendar-Day Simulation Loop...")
    try:
        while True:
            send_heartbeat()
            # Delays heartbeats randomly between 50 and 95 seconds to match natural human keyboard output
            sleep_time = random.randint(50, 95)
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        print("\n[*] Execution stopped safely.")

