from google.oauth2 import service_account
from googleapiclient.discovery import build
from collections import defaultdict
from functools import lru_cache
import json
import os

# Scopes and credentials
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "credentials.json")

# Ranges for fetching data
DETAILS_RANGE = "Kundeinfo!A:B"  # Assuming the new page is named 'Details'
SUMS_RANGE = "A:C"  # For grouped sums
DAYS_CELL = "H21"  # Cell for "Antall dager valgt"


@lru_cache(maxsize=1)
def get_sheets_service():
    """Lazily build and cache the Google Sheets service.

    Looks for credentials in the following order:
    - GOOGLE_APPLICATION_CREDENTIALS env var (path to JSON file)
    - backend/credentials.json next to this file
    """
    # Prefer explicit env var if provided
    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    if creds_json:
        try:
            # Debug: print first 100 chars to see what we're getting
            print(f"🔍 GOOGLE_CREDENTIALS_JSON preview: {creds_json[:100]}...")
            print(f"🔍 Length: {len(creds_json)}")
            print(f"🔍 First 20 chars: {repr(creds_json[:20])}")
            print(f"🔍 Last 20 chars: {repr(creds_json[-20:])}")
            
            # Try to decode as base64 first
            try:
                import base64
                decoded_creds = base64.b64decode(creds_json).decode('utf-8')
                print("✅ Successfully decoded base64 credentials")
                info = json.loads(decoded_creds)
            except:
                # If base64 fails, try direct JSON
                print("🔄 Trying direct JSON parsing")
                info = json.loads(creds_json)
            
            credentials_obj = service_account.Credentials.from_service_account_info(
                info, scopes=SCOPES
            )
            return build("sheets", "v4", credentials=credentials_obj)
        except json.JSONDecodeError as exc:
            print(f"❌ JSON decode error: {exc}")
            print(f"❌ Invalid JSON content: {creds_json[:200]}...")
            raise RuntimeError(f"Invalid GOOGLE_CREDENTIALS_JSON content: {exc}") from exc
        except Exception as exc:
            print(f"❌ Other error: {exc}")
            raise RuntimeError(f"Error processing GOOGLE_CREDENTIALS_JSON: {exc}") from exc

    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if creds_path and os.path.isfile(creds_path):
        credentials_obj = service_account.Credentials.from_service_account_file(
            creds_path, scopes=SCOPES
        )
        return build("sheets", "v4", credentials=credentials_obj)

    # Remove fallback to local credentials.json - only use GitHub Secret
    raise FileNotFoundError(
        "Google service account credentials not found. Set GOOGLE_CREDENTIALS_JSON "
        "environment variable with valid service account JSON."
    )

# Function to fetch data
def fetch_google_data(SPREADSHEET_ID):
    try:
        service = get_sheets_service()
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
        
        # Debug: print what we're getting from Kundeinfo
        print(f"🔍 Kundeinfo data fra Google Sheets:")
        print(f"   Range: {DETAILS_RANGE}")
        print(f"   Raw values: {details_values}")
        
        # Convert details into a dictionary for easy access
        details = {row[0].strip(): row[1].strip() for row in details_values if len(row) > 1}
        
        print(f"   Processed details: {details}")
        print(f"   Details keys: {list(details.keys())}")
        print(f"   Kunde value: '{details.get('Kunde', 'NOT_FOUND')}'")
        print(f"   Prosjekt value: '{details.get('Prosjekt', 'NOT_FOUND')}'")
        print(f"   Versjon value: '{details.get('Versjon', 'NOT_FOUND')}'")
        
        # Debug: check for keys with trailing spaces
        print(f"   Keys with trailing spaces:")
        for key in details.keys():
            if key != key.strip():
                print(f"     '{key}' -> '{key.strip()}' (has trailing space)")
            else:
                print(f"     '{key}' (no trailing space)")

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
            "total_days": int(float(days_value.replace(",", "."))) if days_value and float(days_value.replace(",", ".")).is_integer() else float(days_value.replace(",", ".")) if days_value else None,
            "post_prod_days": int(float(post_prod_days.replace(",", "."))) if post_prod_days and float(post_prod_days.replace(",", ".")).is_integer() else float(post_prod_days.replace(",", ".")) if post_prod_days else None,
            "pre_prod_days": int(float(pre_prod_days.replace(",", "."))) if pre_prod_days and float(pre_prod_days.replace(",", ".")).is_integer() else float(pre_prod_days.replace(",", ".")) if pre_prod_days else None,
            "details": details,
            "company_info": company_info,
            "total_excl_mva": total_excl_mva,
            "total_incl_mva": total_incl_mva,
        }

    except Exception as e:
        # Let callers decide how to handle upstream errors
        raise