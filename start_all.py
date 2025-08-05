import subprocess
import time
import requests
import json
import os
import sys

import gspread
from google.oauth2.service_account import Credentials

# --- Configuration ---
PROJECT_DIR = "C:\\Users\\user\\stream_checker"
PYTHON_EXE = os.path.join(PROJECT_DIR, "venv", "Scripts", "python.exe")
FLASK_APP_SCRIPT = os.path.join(PROJECT_DIR, "mcp_server.py")
NGROK_EXE = os.path.join(PROJECT_DIR, "ngrok.exe")
FLASK_PORT = 3333

# Google Sheet Configuration for URL storage (*** FILL THESE IN ***)
GOOGLE_SHEET_ID_FOR_NGROK_URL = "1mexwRDGRyX41oQdY8K41omLKSvPjZfdRz8mYqCqmg" 
NGROK_CONFIG_WORKSHEET_NAME = "Config"
NGROK_URL_CELL = "B1" 
CREDENTIALS_FILE = os.path.join(PROJECT_DIR, "credentials.json")
# --- End Configuration ---

# Modified start_process to allow selective output capture
def start_process(executable, args, cwd, name, console_window=True, capture_output=False): 
    """Starts a process in the background, optionally in a new console window."""
    print(f"[{name}] Starting process: {executable} {' '.join(args)}")
    creationflags = 0
    if console_window:
        creationflags = subprocess.CREATE_NEW_CONSOLE
    
    stdout_pipe = subprocess.PIPE if capture_output else None # Pipe if capture_output is True
    stderr_pipe = subprocess.PIPE if capture_output else None # Pipe if capture_output is True

    process = subprocess.Popen(
        [executable] + args,
        cwd=cwd,
        stdout=stdout_pipe,
        stderr=stderr_pipe,
        creationflags=creationflags
    )
    print(f"[{name}] Process initiated (PID: {process.pid}).")
    return process

def get_ngrok_public_url_from_output(ngrok_process, timeout_seconds=60):
    """
    Reads ngrok's stdout to find the public URL.
    Returns the HTTPS URL or None if not found within timeout.
    """
    print("[ngrok] Attempting to retrieve public URL from process output...")
    start_time = time.time()
    
    while time.time() - start_time < timeout_seconds:
        line = ngrok_process.stdout.readline()
        if not line:
            time.sleep(0.5)
            if ngrok_process.poll() is not None:
                print(f"ERROR: ngrok process exited prematurely with code {ngrok_process.poll()}")
                print(f"ngrok stderr:\n{ngrok_process.stderr.read().decode('utf-8')}")
                return None
            continue

        line_str = line.decode('utf-8').strip()
        # print(f"[ngrok output] {line_str}") # Uncomment for detailed ngrok output debugging

        if "Forwarding" in line_str and "https://" in line_str:
            try:
                public_url = line_str.split("->")[0].split("https://")[1].strip()
                public_url = "https://" + public_url.split(' ')[0]
                
                print(f"\n{'='*50}\n--- NGROK PUBLIC URL (from output parsing) ---\n{public_url}\n{'='*50}\n")
                return public_url
            except IndexError:
                print(f"WARNING: Could not parse URL from line: {line_str}")
    
    print("ERROR: Failed to retrieve ngrok public URL from process output within timeout.")
    return None

def update_google_sheet_ngrok_url(url):
    """Updates the specified Google Sheet cell with the new ngrok URL."""
    print(f"[Google Sheets] Attempting to update ngrok URL in sheet cell {NGROK_URL_CELL} of '{NGROK_CONFIG_WORKSHEET_NAME}'...")
    try:
        SCOPES = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        creds = Credentials.from_service_account_file(
            CREDENTIALS_FILE,
            scopes=SCOPES
        )
        client = gspread.authorize(creds)
        
        sheet = client.open_by_key(GOOGLE_SHEET_ID_FOR_NGROK_URL).worksheet(NGROK_CONFIG_WORKSHEET_NAME)
        
        sheet.update_acell(NGROK_URL_CELL, url + "/check_tubi")
        print(f"[Google Sheets] Successfully updated ngrok URL in cell {NGROK_URL_CELL}.")
        return True
    except gspread.exceptions.SpreadsheetNotFound:
        print(f"ERROR: [Google Sheets] Spreadsheet ID '{GOOGLE_SHEET_ID_FOR_NGROK_URL}' or worksheet '{NGROK_CONFIG_WORKSHEET_NAME}' not found.")
        print("Please ensure the ID/name is correct and the sheet is shared with your service account email (Editor access).")
        return False
    except Exception as e:
        print(f"ERROR: [Google Sheets] Failed to update Google Sheet with ngrok URL: {e}")
        return False

if __name__ == "__main__":
    print(f"[{os.path.basename(__file__)}] Starting Flask server and ngrok tunnel...")

    # Flask server: Output will be visible in its window
    flask_process = start_process(
        PYTHON_EXE, 
        [FLASK_APP_SCRIPT], 
        PROJECT_DIR, 
        "Flask Server", 
        console_window=True,
        capture_output=False # DON'T capture, so output is visible
    )
    if not flask_process:
        print("Aborting due to Flask server startup failure.")
        sys.exit(1)
    time.sleep(3) # Give Flask a moment to start

    # ngrok tunnel: Output will be CAPTURED (window will be blank) but URL will be obtained
    ngrok_process = start_process(
        NGROK_EXE, 
        ["http", str(FLASK_PORT)], 
        PROJECT_DIR, 
        "ngrok Tunnel", 
        console_window=True,
        capture_output=True # CAPTURE output to get URL, window will be blank
    )
    if not ngrok_process:
        print("Aborting due to ngrok tunnel startup failure.")
        if flask_process.poll() is None:
            flask_process.terminate()
            print("Terminated Flask server.")
        sys.exit(1)
    
    # Get ngrok URL from its captured output
    public_ngrok_base_url = get_ngrok_public_url_from_output(ngrok_process, timeout_seconds=30)

    if public_ngrok_base_url:
        time.sleep(2) # Give Google Sheets a moment (small buffer)
        update_google_sheet_ngrok_url(public_ngrok_base_url)
    else:
        print("WARNING: Could not get ngrok URL. Google Sheet will not be updated.")

    print("\n--- IMPORTANT ---")
    print("The Flask server and ngrok tunnel are now running in their own separate console windows.")
    print("The Flask window should show output. The ngrok window will be blank but its URL is captured.")
    print("These windows must remain open for your application to work.")
    print("To stop them, you will need to manually close their respective console windows or find them in Task Manager and end their processes ('python.exe' and 'ngrok.exe').")
    print("\nThis management script will now exit, but the Flask and ngrok processes will continue.")