import gspread
from google.auth import default
from datetime import datetime, date
import time
import re


class GoogleSheetsReportGenerator:
    def __init__(self, spreadsheet_url):
        """Initialize with Google Sheets URL"""
        self.spreadsheet_url = spreadsheet_url
        self.spreadsheet_id = self.extract_spreadsheet_id(spreadsheet_url)
        self.gc = None
        self.spreadsheet = None
        self.today = datetime.now().date()
        self.today_str = self.today.strftime("%d-%m-%y")
        
        print(f"=== Google Sheets Daily Report Generator ===")
        print(f"Target date: {self.today} ({self.today_str})")
        print(f"Spreadsheet ID: {self.spreadsheet_id}")
        
    def extract_spreadsheet_id(self, url):
        """Extract spreadsheet ID from Google Sheets URL"""
        match = re.search(r'/spreadsheets/d/([a-zA-Z0-9-_]+)', url)
        if match:
            return match.group(1)
        else:
            raise ValueError("Invalid Google Sheets URL")
    
    def authenticate(self):
        print("\n--- Authenticating with Google Sheets API ---")
        try:
            creds, _ = default(scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ])
            self.gc = gspread.authorize(creds)
            print("✓ Authenticated using gcloud application-default credentials")
        except Exception as e:
            print(f"✗ Authentication failed: {e}")
            raise
            
    def connect_to_spreadsheet(self):
        """Connect to the Google Spreadsheet"""
        print(f"\n--- Connecting to spreadsheet ---")
        try:
            self.spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
            print(f"✓ Connected to: {self.spreadsheet.title}")
            
            # List all sheets
            sheet_names = [ws.title for ws in self.spreadsheet.worksheets()]
            print(f"Found {len(sheet_names)} sheets: {', '.join(sheet_names)}")
            return sheet_names
            
        except Exception as e:
            print(f"✗ Failed to connect: {e}")
            raise
    
    def find_fc_column(self, worksheet):
        """Find FC column in the worksheet header"""
        print(f"  → Searching for FC column...")
        
        # Get first few rows to find headers
        header_data = worksheet.get_values('A1:CZ5')  # Check first 5 rows, up to column CZ
        
        for row_idx, row in enumerate(header_data, 1):
            for col_idx, cell_value in enumerate(row, 1):
                if cell_value and str(cell_value).upper().strip() == "FC":
                    col_letter = self.number_to_column_letter(col_idx)
                    print(f"  ✓ Found FC column at {col_letter} (column {col_idx}, header row {row_idx})")
                    return col_idx, col_letter, row_idx
        
        # Fallback
        print("  ! FC header not found, using default column 83 (CG)")
        return 83, 'CG', 1
    
    def number_to_column_letter(self, col_num):
        """Convert column number to Excel-style letter (1=A, 26=Z, 27=AA, etc.)"""
        result = ""
        while col_num > 0:
            col_num -= 1
            result = chr(col_num % 26 + ord('A')) + result
            col_num //= 26
        return result
    
    def parse_date_value(self, cell_value):
        """Parse various date formats to date object"""
        if not cell_value:
            return None
            
        if isinstance(cell_value, (datetime, date)):
            return cell_value if isinstance(cell_value, date) else cell_value.date()
        
        if isinstance(cell_value, str):
            cell_value = cell_value.strip()
            # Try common date formats
            for fmt in ["%d-%m-%y", "%d/%m/%y", "%d.%m.%y", "%Y-%m-%d", 
                       "%d-%m-%Y", "%d/%m/%Y", "%m/%d/%y", "%m/%d/%Y"]:
                try:
                    return datetime.strptime(cell_value, fmt).date()
                except ValueError:
                    continue
        
        return None
    
    def scan_sheet_for_today_data(self, sheet_name):
        """Efficiently scan a sheet for today's data"""
        print(f"\n--- Processing sheet: {sheet_name} ---")
        
        try:
            worksheet = self.spreadsheet.worksheet(sheet_name)
            print(f"  → Sheet loaded successfully")
            
            # Find FC column
            fc_col_num, fc_col_letter, header_row = self.find_fc_column(worksheet)
            data_start_row = header_row + 1
            
            # Get FC column data efficiently
            print(f"  → Fetching FC column data starting from row {data_start_row}...")
            fc_range = f"{fc_col_letter}{data_start_row}:{fc_col_letter}"
            fc_values = worksheet.get_values(fc_range)
            
            if not fc_values:
                print(f"  ! No data found in FC column")
                return []
            
            print(f"  → Got {len(fc_values)} cells from FC column")
            
            # Find rows with today's date
            today_rows = []
            for idx, row in enumerate(fc_values):
                if row:  # Non-empty row
                    cell_value = row[0] if row else None
                    if cell_value:
                        parsed_date = self.parse_date_value(cell_value)
                        if parsed_date == self.today:
                            actual_row = data_start_row + idx
                            today_rows.append(actual_row)
                            print(f"  ✓ Found today's date in row {actual_row}: {cell_value}")
            
            if not today_rows:
                print(f"  ! No entries found for today ({self.today_str})")
                return []
            
            print(f"  → Found {len(today_rows)} rows with today's date")
            
            # Efficiently fetch Name, Phone, Comment for today's rows
            contacts_data = []
            
            for row_num in today_rows:
                # Fetch A, B, C columns for this specific row
                range_name = f"A{row_num}:C{row_num}"
                print(f"  → Fetching data from {range_name}...")
                
                row_data = worksheet.get_values(range_name)
                if row_data and row_data[0]:
                    data_row = row_data[0]
                    name = data_row[0] if len(data_row) > 0 else ""
                    phone = data_row[1] if len(data_row) > 1 else ""
                    comment = data_row[2] if len(data_row) > 2 else ""
                    
                    contact = {
                        'sheet': sheet_name,
                        'row': row_num,
                        'name': name,
                        'phone': phone,
                        'comment': comment,
                        'date': self.today_str
                    }
                    contacts_data.append(contact)
                    
                    print(f"    ✓ Row {row_num}: {name} | {phone} | {comment}")
                
                # Small delay to avoid rate limits
                time.sleep(0.1)
            
            print(f"  ✓ Extracted {len(contacts_data)} contacts from {sheet_name}")
            return contacts_data
            
        except Exception as e:
            print(f"  ✗ Error processing sheet {sheet_name}: {e}")
            return []
    
    def get_sheets_to_process(self, all_sheets):
        """Get list of sheets to process (exclude Daily Report and Approved)"""
        excluded_sheets = ["Daily Report", "Approved"]
        available_sheets = [sheet for sheet in all_sheets if sheet not in excluded_sheets]
        
        print(f"\n=== Available sheets to scan ===")
        for i, sheet_name in enumerate(available_sheets, 1):
            print(f"{i}. {sheet_name}")
        
        print(f"\nWhich sheets should I scan for today's contacts?")
        print("Enter sheet numbers (e.g., 1,3,5) or 'all' for all sheets:")
        
        user_input = input("Your choice: ").strip().lower()
        
        if user_input == 'all':
            return available_sheets
        else:
            try:
                selected_numbers = [int(x.strip()) for x in user_input.split(',')]
                selected_sheets = [available_sheets[i-1] for i in selected_numbers 
                                 if 1 <= i <= len(available_sheets)]
                return selected_sheets
            except (ValueError, IndexError):
                print("Invalid input. Processing all sheets...")
                return available_sheets
    
    def write_to_daily_report(self, all_contacts):
        """Write collected contacts to Daily Report sheet"""
        print(f"\n--- Writing to Daily Report sheet ---")
        
        if not all_contacts:
            print("! No contacts to write")
            return
        
        try:
            # Get Daily Report sheet
            daily_report_sheet = self.spreadsheet.worksheet("Daily Report")
            print(f"  ✓ Connected to Daily Report sheet")
            
            # Clear existing data (keep headers in row 1)
            print(f"  → Clearing existing data...")
            daily_report_sheet.clear()
            
            # Write headers
            headers = ["Name", "Phone", "Comment", "Date", "Source Sheet", "Source Row"]
            daily_report_sheet.append_row(headers)
            print(f"  ✓ Added headers")
            
            # Prepare data for batch write
            data_rows = []
            for contact in all_contacts:
                row = [
                    contact['name'],
                    contact['phone'], 
                    contact['comment'],
                    contact['date'],
                    contact['sheet'],
                    contact['row']
                ]
                data_rows.append(row)
            
            # Batch write all data
            if data_rows:
                print(f"  → Writing {len(data_rows)} contacts...")
                daily_report_sheet.append_rows(data_rows)
                print(f"  ✓ Successfully wrote {len(data_rows)} contacts to Daily Report")
            
        except Exception as e:
            print(f"  ✗ Error writing to Daily Report: {e}")
    
    def generate_report(self):
        """Main function to generate the daily report"""
        start_time = time.time()
        
        try:
            # Authenticate and connect
            self.authenticate()
            all_sheets = self.connect_to_spreadsheet()
            
            # Get sheets to process
            sheets_to_process = self.get_sheets_to_process(all_sheets)
            print(f"\n=== Will process {len(sheets_to_process)} sheets ===")
            print(', '.join(sheets_to_process))
            
            # Process each sheet
            all_contacts = []
            for sheet_name in sheets_to_process:
                contacts = self.scan_sheet_for_today_data(sheet_name)
                all_contacts.extend(contacts)
                print(f"  → Running total: {len(all_contacts)} contacts")
            
            # Write to Daily Report sheet
            self.write_to_daily_report(all_contacts)
            
            # Summary
            elapsed = time.time() - start_time
            print(f"\n=== SUMMARY ===")
            print(f"✓ Processed {len(sheets_to_process)} sheets")
            print(f"✓ Found {len(all_contacts)} contacts for {self.today_str}")
            print(f"✓ Updated Daily Report sheet")
            print(f"⏱ Total time: {elapsed:.2f} seconds")
            
            if all_contacts:
                print(f"\nContacts found:")
                for contact in all_contacts:
                    print(f"  • {contact['name']} ({contact['phone']}) - {contact['sheet']}")
        
        except Exception as e:
            print(f"✗ Script failed: {e}")
            import traceback
            traceback.print_exc()


def main():
    # Your Google Sheets URL
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1wA3ktIPXsidmNe8IVR24Rk_kP78wZ9giVlhnDu104Fg/edit?usp=sharing"
    
    generator = GoogleSheetsReportGenerator(spreadsheet_url)
    generator.generate_report()
    
    print("\nPress Enter to exit...")
    input()


if __name__ == "__main__":
    main()