import pandas as pd
import re

def normalize_number(num):
    """Convert phone number to plain digits string (removes +, spaces, dashes)."""
    if pd.isna(num):
        return None
    return re.sub(r"\D", "", str(num))  # keep only digits

def check_blacklist(file_numbers, google_sheet_url, output_filename="cleaned_phone_numbers.xlsx"):
    # Read all data from Excel file (keeping all columns)
    numbers_df = pd.read_excel(file_numbers)

    print(f"Loaded {len(numbers_df)} rows from input file.")
    print(f"Columns found: {list(numbers_df.columns)}")
    
    # Read blacklist from Google Sheet (phone numbers in second column)
    blacklist_df = pd.read_csv(google_sheet_url, header=None, usecols=[1])
    
    # Create normalized phone number column for comparison
    # Assuming phone numbers are in the second column (index 1)
    phone_column = numbers_df.iloc[:, 1]  # Second column
    normalized_phones = phone_column.apply(normalize_number)
    
    # Normalize blacklist numbers
    blacklist_df[1] = blacklist_df[1].apply(normalize_number)
    blacklist_df = blacklist_df.dropna()
    blacklist_set = set(blacklist_df[1])
    
    print(f"Loaded {len(blacklist_set)} numbers from blacklist.")
    
    # Find matches
    matches = []
    blacklisted_indices = []
    
    for idx, norm_phone in enumerate(normalized_phones):
        if norm_phone and norm_phone in blacklist_set:
            matches.append(norm_phone)
            blacklisted_indices.append(idx)
    
    # Report results
    print(f"\nFound {len(matches)} matching phone numbers.")
    if matches:
        print("DO NOT CALL these numbers:", sorted(set(matches)))
        print(f"Removing {len(blacklisted_indices)} rows from dataset...")
        
        # Create cleaned dataset (remove blacklisted rows)
        cleaned_df = numbers_df.drop(blacklisted_indices).reset_index(drop=True)
        
        # Save cleaned dataset
        cleaned_df.to_excel(output_filename, index=False)
        print(f"Cleaned dataset saved as '{output_filename}' with {len(cleaned_df)} rows.")
        
        # Show some examples of removed entries (first few)
        print(f"\nExample of removed entries (showing first 3):")
        removed_df = numbers_df.iloc[blacklisted_indices[:3]]
        for idx, row in removed_df.iterrows():
            print(f"  Row {idx}: {row.iloc[1]} (and associated data)")
            
    else:
        print("No matches found. All numbers are clean!")
        # Still save the original file as cleaned version
        numbers_df.to_excel(output_filename, index=False)
        print(f"Original dataset saved as '{output_filename}' (no changes needed).")
    
    return len(matches)

def check_blacklist_custom_column(file_numbers, google_sheet_url, phone_column_index=1, 
                                output_filename="cleaned_phone_numbers.xlsx"):
    """
    Enhanced version that allows specifying which column contains phone numbers.
    
    Args:
        file_numbers: Path to Excel file
        google_sheet_url: URL to Google Sheet CSV
        phone_column_index: Index of column containing phone numbers (0-based)
        output_filename: Name of output Excel file
    """
    # Read all data from Excel file
    numbers_df = pd.read_excel(file_numbers)
    
    # Validate column index
    if phone_column_index >= len(numbers_df.columns):
        raise ValueError(f"Phone column index {phone_column_index} is out of range. File has {len(numbers_df.columns)} columns.")
    
    print(f"Loaded {len(numbers_df)} rows from input file.")
    print(f"Using column {phone_column_index} ('{numbers_df.columns[phone_column_index]}') for phone numbers.")
    
    # Read blacklist from Google Sheet
    blacklist_df = pd.read_csv(google_sheet_url, header=None, usecols=[1])
    
    # Normalize phone numbers
    phone_column = numbers_df.iloc[:, phone_column_index]
    normalized_phones = phone_column.apply(normalize_number)
    
    # Normalize blacklist
    blacklist_df[0] = blacklist_df[0].apply(normalize_number)
    blacklist_df = blacklist_df.dropna()
    blacklist_set = set(blacklist_df[0])
    
    print(f"Loaded {len(blacklist_set)} numbers from blacklist.")
    
    # Find matches
    matches = []
    blacklisted_indices = []
    
    for idx, norm_phone in enumerate(normalized_phones):
        if norm_phone and norm_phone in blacklist_set:
            matches.append(norm_phone)
            blacklisted_indices.append(idx)
    
    # Report and save results
    print(f"\nFound {len(matches)} matching phone numbers.")
    if matches:
        print("DO NOT CALL these numbers:", sorted(set(matches)))
        
        cleaned_df = numbers_df.drop(blacklisted_indices).reset_index(drop=True)
        cleaned_df.to_excel(output_filename, index=False)
        print(f"Cleaned dataset saved as '{output_filename}' with {len(cleaned_df)} rows (removed {len(blacklisted_indices)}).")
    else:
        print("No matches found. All numbers are clean!")
        numbers_df.to_excel(output_filename, index=False)
        print(f"Original dataset saved as '{output_filename}' (no changes needed).")
    
    return len(matches)

# Example usage:
if __name__ == "__main__":
    sheet_id = "1Dr3f-uyVGLNL656WJbYJF-p6Ja9ucy4vzNTVfjihCVE"
    google_sheet_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv"
    
    # Basic usage (assumes phone numbers are in second column - index 1)
    check_blacklist("phone_numbers_to_check.xlsx", google_sheet_url, "cleaned_contacts.xlsx")
    
    # Advanced usage (specify custom column for phone numbers)
    # check_blacklist_custom_column("phone_numbers_to_check.xlsx", google_sheet_url, 
    #                              phone_column_index=2, output_filename="cleaned_contacts.xlsx")