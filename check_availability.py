import asyncio
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from playwright.async_api import async_playwright

# Google Sheets setup
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name("your_credentials.json", SCOPE)
gc = gspread.authorize(CREDS)

SHEET_NAME = "Google Sheet Streaming Checker"
WORKSHEET_NAME = "Tubi"
sheet = gc.open(SHEET_NAME).worksheet(WORKSHEET_NAME)

# Load data
data = sheet.get_all_records()
START_ROW = 2  # Adjust if you have headers

async def check_movie_availability(playwright):
    browser = await playwright.chromium.launch(headless=False)  # Show browser for visual verification
    context = await browser.new_context()
    page = await context.new_page()

    for i, row in enumerate(data, start=START_ROW):
        link = row['Tubi Link'] if 'Tubi Link' in row else row['Link']
        country = row['Country'] if 'Country' in row else row.get('D', 'Unknown')
        
        if not link or "tubitv.com" not in link:
            sheet.update_cell(i + 1, 5, "Invalid or Missing Link")
            continue

        try:
            await page.goto(f"http://scraperapi.com?api_key=5da6a435c89f56b1ef3f4541d2c6d9bc&url={link}", timeout=60000)
            await page.wait_for_timeout(5000)  # Let page load

            # UI-based checks
            has_video_player = await page.locator("video").is_visible()
            has_controls = await page.locator("video[controls]").count() > 0
            is_playable = await page.locator("button:has-text('Play'), button:has-text('Watch Now')").count() > 0

            if has_video_player or has_controls or is_playable:
                result = "✅ Available"
            else:
                result = "❌ Not Playable"

            sheet.update_cell(i + 1, 5, result)  # Column E for result

        except Exception as e:
            sheet.update_cell(i + 1, 5, f"Error: {str(e)[:30]}")

    await browser.close()

async def main():
    async with async_playwright() as playwright:
        await check_movie_availability(playwright)

asyncio.run(main())
