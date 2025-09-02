import pandas as pd
import re

def normalize_number(num):
    """Convert phone number to plain digits string (removes +, spaces, dashes)."""
    if pd.isna(num):
        return None
    return re.sub(r"\D", "", str(num))  # keep only digits

def check_blacklist(file_numbers, file_blacklist):
    # Read phone numbers from first column, blacklist from second column
    numbers_df = pd.read_excel(file_numbers, header=None, usecols=[0])
    blacklist_df = pd.read_excel(file_blacklist, header=None, usecols=[1])
   
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

# Run the checker
check_blacklist("phone_numbers_to_check.xlsx", "blacklist.xlsx")