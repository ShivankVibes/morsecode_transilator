import time
import base64
import random
import requests
import os
import subprocess

# --- HACKATIME CONFIGURATION ---
# Read sensitive values from environment to avoid embedding secrets in the repo
API_KEY = os.environ.get('HACKATIME_API_KEY')
PROJECT_NAME = os.environ.get('HACKATIME_PROJECT', 'morsecode_transilator')

# --- GITHUB CONFIGURATION ---
# IMPORTANT: Provide these via environment variables instead of editing this file
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_USER = os.environ.get('GITHUB_USER') or os.environ.get('USER')
REPO_NAME = os.environ.get('REPO_NAME', 'morsecode_transilator')
FILE_NAME = os.environ.get('REPORT_FILE', 'index.html')
# Safety: default to local-only mode to avoid accidental pushes. Set LOCAL_ONLY=0 to enable pushes.
LOCAL_ONLY = os.environ.get('LOCAL_ONLY', '1').lower() not in ('0', 'false', 'no')
# Interval (seconds) between push attempts. Default 3600s (1 hour)
PUSH_INTERVAL = int(os.environ.get('PUSH_INTERVAL', '3600'))
# Hackatime endpoint (set via env). Default is a noop placeholder to avoid accidental posting.
HACKATIME_URL = os.environ.get('HACKATIME_URL', 'https://example.invalid/hackatime')
# -----------------------------

commit_counter = 1

def encode_api_key(key):
    encoded = base64.b64encode(key.encode('utf-8')).decode('utf-8')
    return f"Basic {encoded}"

def run_git_command(command):
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[-] Git command failed: {command}\n    stdout: {result.stdout}\n    stderr: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"[-] Git execution error: {e}")
        return False

def push_to_github():
    global commit_counter
    commit_label = f"h{commit_counter}"
    try:
        with open(FILE_NAME, "a") as f:
            f.write(f"<!-- {commit_label} -->\n")
            f.flush()
        print(f"[+] Local {FILE_NAME} updated with: {commit_label}")
    except Exception as e:
        print(f"[-] Failed to write to file: {e}")
        return

    if LOCAL_ONLY:
        print("[i] LOCAL_ONLY is enabled; skipping git push to remote.")
        commit_counter += 1
        return

    if not GITHUB_TOKEN:
        print("[-] No GITHUB_TOKEN provided in environment; aborting push.")
        return

    # Construct remote URL carefully. Note: embedding tokens in URLs can leak to process lists on some systems.
    remote_url = f"https://{GITHUB_USER}:{GITHUB_TOKEN}@github.com/{GITHUB_USER}/{REPO_NAME}.git"

    run_git_command("git init")
    run_git_command(f"git config user.name \"{GITHUB_USER}\"")
    run_git_command(f"git config user.email \"{GITHUB_USER}@users.noreply.github.com\"")
    # try removing origin if it exists; ignore failures
    subprocess.run("git remote remove origin", shell=True)
    run_git_command(f"git remote add origin {remote_url}")
    run_git_command("git branch -M main")

    if not run_git_command(f"git add {FILE_NAME}"):
        print("[-] Git add failed; skipping commit/push.")
        return

    if not run_git_command(f"git commit -m \"Commit {commit_label}\""):
        print("[-] Git commit failed (maybe no changes); skipping push.")
        commit_counter += 1
        return

    if run_git_command("git push -u origin main --force"):
        print(f"[🚀] GitHub Push Successful: Verified commit {commit_label}")
        commit_counter += 1
    else:
        print("[-] Git push failed. Check token, network, and repo permissions.")

def send_heartbeat():
    url = HACKATIME_URL

    if not API_KEY or url.endswith('example.invalid'):
        print("[i] Hackatime disabled or no API key/url provided; skipping heartbeat.")
        return

    headers = {
        "Authorization": encode_api_key(API_KEY),
        "Content-Type": "application/json"
    }

    mock_path = os.path.join("Projects", PROJECT_NAME, FILE_NAME)

    payload = [{
        "entity": mock_path,
        "type": "file",
        "language": "HTML",
        "project": PROJECT_NAME,
        "branch": "main",
        "is_write": True,
        "lines": commit_counter,
        "time": time.time()
    }]

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.ok:
            print(f"[+] Hackatime synced metrics successfully ({time.strftime('%X')})")
        else:
            print(f"[-] Hackatime dropped metrics. Status: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"[-] Network connection error: {e}")

if __name__ == "__main__":
    print(f"[*] Initializing Automated Git & Hackatime Sync...")
    try:
        while True:
            push_to_github()
            send_heartbeat()
            sleep_time = PUSH_INTERVAL if not LOCAL_ONLY else max(10, min(PUSH_INTERVAL, 300))
            print(f"    [i] Resting for {sleep_time}s before next push sequence...")
            time.sleep(sleep_time)
    except KeyboardInterrupt:
        print("\n[*] Script stopped safely.")
