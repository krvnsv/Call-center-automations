import pandas as pd
import re

def normalize_number(num):
    """Convert phone number to plain digits string (removes +, spaces, dashes)."""
    if pd.isna(num):
        return None
    return re.sub(r"\D", "", str(num))  # keep only digits

def check_blacklist(file_numbers, google_sheet_url):
    # Read phone numbers from first column (local Excel file)
    numbers_df = pd.read_excel(file_numbers, header=None, usecols=[0])
   
    # Read blacklist from Google Sheet (public view-only CSV)
    blacklist_df = pd.read_csv(google_sheet_url, header=None, usecols=[1])
   
    # Normalize both columns
    numbers_df[0] = numbers_df[0].apply(normalize_number)
    blacklist_df[1] = blacklist_df[1].apply(normalize_number)
   
    # Drop empty values
    numbers_df = numbers_df.dropna()
    blacklist_df = blacklist_df.dropna()
   
    # Convert to sets
    numbers_set = set(numbers_df[0])
    blacklist_set = set(blacklist_df[1])
   
    # Find intersection
    matches = numbers_set.intersection(blacklist_set)
   
    print(f"Found {len(matches)} matching phone numbers.")
    if matches:
        print("DO NOT CALL these numbers:", sorted(matches))
    else:
        print("No matches found.")

# Example usage:
sheet_id = "1Dr3f-uyVGLNL656WJbYJF-p6Ja9ucy4vzNTVfjihCVE"
google_sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"

check_blacklist("phone_numbers_to_check.xlsx", google_sheet_url)