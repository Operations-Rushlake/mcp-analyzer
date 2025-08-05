import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 🔐 Use your actual JSON file name here
CREDENTIALS_FILE = "filmchecker-466213-542665494bdc.json"

# Connect to Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)

# 📄 Open your Google Sheet (adjust the name if needed)
spreadsheet = client.open("Google Sheet Streaming Checker")
sheet = spreadsheet.worksheet("Tubi")

# Read and print all rows
data = sheet.get_all_values()
for row in data:
    print(row)

