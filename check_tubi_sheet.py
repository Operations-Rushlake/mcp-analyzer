import gspread
import requests
from oauth2client.service_account import ServiceAccountCredentials

# Sheet configuration
# Use the Unique ID (Spreadsheet ID) directly
SPREADSHEET_ID = "1mexwrRDGRyXA1qOdY8kG41omLkSVpJzfdRz8mYaCqmg" # <<< Changed to use the ID from your URL
WORKSHEET_NAME = "Tubi"  # Keep this as your actual sheet tab name

# Flask API URL (local or via ngrok)
API_URL = "http://127.0.0.1:3333/check_tubi"  # Change to ngrok URL if deployed externally

# Google Sheets authentication
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Open sheet using the Spreadsheet ID
try:
    sheet = client.open_by_key(SPREADSHEET_ID).worksheet(WORKSHEET_NAME) # <<< Changed to open_by_key
    print(f"Successfully opened Google Sheet with ID: {SPREADSHEET_ID} and Worksheet: {WORKSHEET_NAME}")
except gspread.exceptions.SpreadsheetNotFound:
    print(f"Error: Google Sheet with ID '{SPREADSHEET_ID}' not found.")
    print("Please ensure the ID is correct and the sheet is shared with your service account email.")
    exit()
except gspread.exceptions.WorksheetNotFound:
    print(f"Error: Worksheet (tab) named '{WORKSHEET_NAME}' not found in the spreadsheet.")
    print("Please ensure the worksheet name is correct and case-sensitive.")
    exit()
except Exception as e:
    print(f"An unexpected error occurred while accessing the sheet: {e}")
    exit()

rows = sheet.get_all_records()

# Get headers
header = sheet.row_values(1)
try:
    platform_idx = header.index("Platform") + 1
    link_idx = header.index("Tubi Link") + 1
    territory_idx = header.index("Territories") + 1
    available_idx = header.index("is this Film Online?") + 1
except ValueError as e:
    print(f"Error: Missing expected header column. Please ensure all required columns ('Platform', 'Tubi Link', 'Territories', 'is this Film Online?') exist in your sheet. Error: {e}")
    exit()


# Process rows
for i, row in enumerate(rows, start=2):  # Row 2 onward (assuming first row is header)
    platform = row.get("Platform", "").strip().lower()
    tubi_url = row.get("Tubi Link", "").strip()
    territory = row.get("Territories", "").strip()
    current_status = row.get("is this Film Online?")

    # Only process if platform is tubi and 'is this Film Online?' is not already True
    # If you want to re-check all, remove `and not current_status`
    if platform == "tubi" and not current_status:
        print(f"Checking row {i}: Title='{row.get('Title', 'N/A')}', Tubi Link='{tubi_url}'")

        payload = {
            "tubi_url": tubi_url,
            "territory": territory
        }

        try:
            response = requests.post(API_URL, json=payload, timeout=45)
            response.raise_for_status()
            result = response.json()
            available = result.get("available", False)
            sheet.update_cell(i, available_idx, str(available)) # Update the cell with the boolean as a string
            print(f"Updated row {i} - Availability: {available}")
        except requests.exceptions.Timeout:
            print(f"Error checking row {i}: Request timed out after 45 seconds.")
            sheet.update_cell(i, available_idx, "Timeout")
        except requests.exceptions.RequestException as e:
            print(f"Error checking row {i}: HTTP/Network error: {e}")
            sheet.update_cell(i, available_idx, "Error")
        except Exception as e:
            print(f"An unexpected error occurred for row {i}: {e}")
            sheet.update_cell(i, available_idx, "Error")

print("Sheet update process completed.")