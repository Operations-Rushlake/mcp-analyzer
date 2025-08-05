import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)
gc = gspread.authorize(creds)

spreadsheet_id = "1mexwrRDGRyXA1qOdY8kG41omLkSVpJzfdRz8mYaCqmg"
sh = gc.open_by_key(spreadsheet_id)
worksheet = sh.worksheet("Config")

try:
    worksheet.update_acell("B1", "https://test-ngrok-url.com")
    print("✅ Successfully updated cell B1.")
except Exception as e:
    print("❌ Error occurred:", str(e))

