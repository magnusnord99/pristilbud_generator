from google.oauth2 import service_account
from googleapiclient.discovery import build
from collections import defaultdict

# Scopes and credentials
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
SERVICE_ACCOUNT_FILE = "/Users/magnusnordmo/Desktop/Pristilbud_generator/credentials.json"
  # Your Google Sheets ID

# Ranges for fetching data
DETAILS_RANGE = "Kundeinfo!A:B"  # Assuming the new page is named 'Details'
SUMS_RANGE = "A:C"  # For grouped sums
DAYS_CELL = "H21"  # Cell for "Antall dager valgt"


# Authenticate
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
service = build("sheets", "v4", credentials=credentials)

# Function to fetch data
def fetch_google_data(SPREADSHEET_ID):
    try:
        sheet = service.spreadsheets()

        # Fetch grouped sums data (A:C)
        sums_result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=SUMS_RANGE).execute()
        sums_values = sums_result.get("values", [])

        grouped_sums = defaultdict(float)
        current_category = None
        total_excl_mva = None
        total_incl_mva = None

        # Fetch "Antall dager valgt" from H21
        days_result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=DAYS_CELL).execute()
        days_value = days_result.get("values", [[None]])[0][0]  # Get the value or None if empty

        # Fetch Post produksjon days (H23) and Oppstart/planlegging days (H24)
        post_prod_days_result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="H23").execute()
        post_prod_days = post_prod_days_result.get("values", [[None]])[0][0]

        pre_prod_days_result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="H24").execute()
        pre_prod_days = pre_prod_days_result.get("values", [[None]])[0][0]

        # Fetch project and customer details from Kundeinfo!A:B
        details_result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range=DETAILS_RANGE).execute()
        details_values = details_result.get("values", [])

        # Fetch company info from Kundeinfo!D:E
        company_info_result = sheet.values().get(spreadsheetId=SPREADSHEET_ID, range="Kundeinfo!D:E").execute()
        company_info_values = company_info_result.get("values", [])

        # Convert company info into a dictionary
        company_info = {}
        current_label = None

        for row in company_info_values:
            if len(row) > 0 and row[0].strip():  # If the first column (label) is not empty
                current_label = row[0].strip()  # Use it as the current label
                company_info[current_label] = row[1].strip() if len(row) > 1 and row[1].strip() else " "
            elif current_label and len(row) > 1:  # If the first column is empty, append to the current label
                company_info[current_label] += f"\n{row[1].strip()}" if row[1].strip() else ""

        # Convert details into a dictionary for easy access
        details = {row[0].strip(): row[1].strip() for row in details_values if len(row) > 1}

        for row in sums_values:
            if len(row) > 2:  # Ensure row has A, B, and C values
                unit = row[0].strip() if row[0] else None  # Column A
                number = row[2].replace(",", ".")  # Column C

                if number.replace(".", "", 1).isdigit():  # Check if it's a number
                    number = float(number)

                    # Extract totals for eksl. mva and inkl. mva
                    if unit == "Produksjon totalt eksl. mva":
                        total_excl_mva = number
                    elif unit == "Produksjon totalt inkl. mva":
                        total_incl_mva = number

                    if unit:  # New category
                        current_category = unit
                    if current_category:
                        grouped_sums[current_category] += number

        # Convert defaultdict to a sorted list of tuples
        grouped_sums_list = sorted(grouped_sums.items(), key=lambda x: x[0])

        return {
            "grouped_sums": grouped_sums_list,
            "total_days": int(days_value) if days_value and days_value.isdigit() else None,
            "post_prod_days": int(post_prod_days) if post_prod_days and post_prod_days.isdigit() else None,
            "pre_prod_days": int(pre_prod_days) if pre_prod_days and pre_prod_days.isdigit() else None,
            "details": details,
            "company_info": company_info,
            "total_excl_mva": total_excl_mva,
            "total_incl_mva": total_incl_mva,
        }

    except Exception as e:
        print(f"Failed to access the spreadsheet: {e}")
        return None