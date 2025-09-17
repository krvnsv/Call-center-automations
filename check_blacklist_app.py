import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd
import re
import os
import threading
import time

# === Normalization function ===
def normalize_number(num):
    if pd.isna(num):
        return None
    return re.sub(r"\D", "", str(num))  # keep only digits

# === Helper function to find phone column ===
def find_phone_column(df):
    phone_indicators = ['phone', 'tel', 'number', 'mobile', 'cell', 'contact', '/', 'broj']
    for col_idx, col_name in enumerate(df.columns):
        col_name_lower = str(col_name).lower()
        if any(indicator in col_name_lower for indicator in phone_indicators):
            return col_idx, col_name
    for col_idx in range(min(5, len(df.columns))):
        sample_data = df.iloc[:20, col_idx].dropna()
        phone_like_count = 0
        for value in sample_data:
            normalized = normalize_number(value)
            if normalized and 6 <= len(normalized) <= 15:
                phone_like_count += 1
        if len(sample_data) > 0 and phone_like_count / len(sample_data) > 0.7:
            return col_idx, df.columns[col_idx]
    return 1, df.columns[1] if len(df.columns) > 1 else df.columns[0]

# === Helper function to extract Google Sheet ID ===
def extract_sheet_id(url_or_id):
    """Extract Google Sheet ID from URL or validate if it's already an ID"""
    # If it's already just an ID (alphanumeric string)
    if re.match(r'^[a-zA-Z0-9_-]+$', url_or_id.strip()) and len(url_or_id.strip()) > 20:
        return url_or_id.strip()
    
    # Extract from full Google Sheets URL
    patterns = [
        r'/spreadsheets/d/([a-zA-Z0-9-_]+)',
        r'id=([a-zA-Z0-9-_]+)',
        r'/d/([a-zA-Z0-9-_]+)/'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    
    return None

# === Core cleaning function ===
def check_blacklist(file_numbers, google_sheet_urls, output_folder, status_callback=None):
    def update_status(message):
        if status_callback:
            status_callback(message)
    try:
        update_status("📄 Loading input file...")
        time.sleep(0.5)
        if file_numbers.endswith(".xlsx"):
            numbers_df = pd.read_excel(file_numbers)
        elif file_numbers.endswith(".csv"):
            numbers_df = pd.read_csv(file_numbers)
        else:
            raise ValueError("Unsupported file format. Please use .xlsx or .csv")
        update_status(f"✅ Loaded {len(numbers_df)} rows from input file")
        phone_col_idx, phone_col_name = find_phone_column(numbers_df)
        update_status(f"📱 Detected phone column: '{phone_col_name}' (column {phone_col_idx + 1})")
        time.sleep(0.3)
        update_status("🌐 Downloading blacklist from Google Sheet...")
        time.sleep(0.5)
        blacklist_df = None
        for url in google_sheet_urls:
            try:
                blacklist_df = pd.read_csv(url, header=None, usecols=[1])
                break
            except Exception:
                continue
        
        if blacklist_df is None:
            raise Exception("Could not connect to Google Sheet blacklist")

        phone_column = numbers_df.iloc[:, phone_col_idx]
        normalized_phones = phone_column.apply(normalize_number)
        blacklist_df[1] = blacklist_df[1].apply(normalize_number)
        blacklist_df = blacklist_df.dropna()
        blacklist_set = set(blacklist_df[1])
        update_status(f"✅ Loaded {len(blacklist_set)} numbers from blacklist")
        time.sleep(0.3)
        update_status("🔍 Comparing phone numbers...")
        time.sleep(0.5)
        blacklisted_indices = [
            idx for idx, norm_phone in enumerate(normalized_phones)
            if norm_phone and norm_phone in blacklist_set
        ]
        update_status(f"⚠️  Found {len(blacklisted_indices)} matches to remove")
        time.sleep(0.3)
        update_status("📝 Creating cleaned dataset...")
        cleaned_df = numbers_df.drop(blacklisted_indices).reset_index(drop=True)
        removed_df = numbers_df.iloc[blacklisted_indices]
        base_name = os.path.splitext(os.path.basename(file_numbers))[0]
        cleaned_path = os.path.join(output_folder, f"{base_name}_cleaned.xlsx")
        removed_path = os.path.join(output_folder, f"{base_name}_removed.xlsx")
        update_status("💾 Saving files...")
        cleaned_df.to_excel(cleaned_path, index=False)
        removed_df.to_excel(removed_path, index=False)
        time.sleep(0.3)
        update_status("✅ Processing complete!")
        return len(blacklisted_indices), cleaned_path, removed_path
    except Exception as e:
        update_status(f"❌ Error: {str(e)}")
        raise

# === GUI ===
def run_app():
    root = tk.Tk()
    root.title("Excel/CSV Blacklist Cleaner v2.1")
    root.geometry("1280x800")
    root.configure(bg="#f0f0f0")
    root.resizable(True, True)

    # Header
    header_frame = tk.Frame(root, bg="#2c3e50", height=60)
    header_frame.pack(fill=tk.X, padx=10, pady=(10, 0))
    header_frame.pack_propagate(False)
    
    title_label = tk.Label(header_frame, text="📞 Blacklist Phone Number Cleaner", 
                          font=("Arial", 16, "bold"), fg="white", bg="#2c3e50")
    title_label.pack(expand=True)

    # Main content frame
    main_frame = tk.Frame(root, bg="#f0f0f0")
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Google Sheets URL section
    sheets_frame = tk.Frame(main_frame, bg="white", relief=tk.RAISED, bd=1)
    sheets_frame.pack(fill=tk.X, pady=(0, 10))
    
    tk.Label(sheets_frame, text="🌐 Provide Google Sheets Link to Your Blacklist (make sure Google Sheets is link shared):", 
             font=("Arial", 11, "bold"), bg="white").pack(pady=(10, 2), anchor=tk.W, padx=10)
    
    tk.Label(sheets_frame, text="If you are in team Brian, provide Blok Lista Brian URL", 
             font=("Arial", 9, "italic"), fg="#666666", bg="white").pack(pady=(0, 5), anchor=tk.W, padx=10)
    
    sheets_entry_frame = tk.Frame(sheets_frame, bg="white")
    sheets_entry_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    entry_sheets = tk.Entry(sheets_entry_frame, width=80, font=("Arial", 10))
    entry_sheets.pack(side=tk.LEFT, fill=tk.X, expand=True)

    # File selection section
    file_frame = tk.Frame(main_frame, bg="white", relief=tk.RAISED, bd=1)
    file_frame.pack(fill=tk.X, pady=(0, 10))
    
    tk.Label(file_frame, text="📁 Select Input File (Excel or CSV):", 
             font=("Arial", 11, "bold"), bg="white").pack(pady=(10, 5), anchor=tk.W, padx=10)
    
    file_entry_frame = tk.Frame(file_frame, bg="white")
    file_entry_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    entry_file = tk.Entry(file_entry_frame, width=60, font=("Arial", 10))
    entry_file.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def select_file():
        filename = filedialog.askopenfilename(
            title="Select Excel or CSV File",
            filetypes=[("Excel/CSV Files", "*.xlsx *.csv"), ("Excel Files", "*.xlsx"), ("CSV Files", "*.csv")]
        )
        if filename:
            entry_file.delete(0, tk.END)
            entry_file.insert(0, filename)

    btn_browse = tk.Button(file_entry_frame, text="Browse", command=select_file,
                           bg="#3498db", fg="white", font=("Arial", 10))
    btn_browse.pack(side=tk.RIGHT, padx=(5, 0))

    # Output folder section
    output_frame = tk.Frame(main_frame, bg="white", relief=tk.RAISED, bd=1)
    output_frame.pack(fill=tk.X, pady=(0, 10))
    
    tk.Label(output_frame, text="📂 Output Folder (optional - defaults to input file location):", 
             font=("Arial", 11, "bold"), bg="white").pack(pady=(10, 5), anchor=tk.W, padx=10)
    
    output_entry_frame = tk.Frame(output_frame, bg="white")
    output_entry_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
    
    entry_out = tk.Entry(output_entry_frame, width=60, font=("Arial", 10))
    entry_out.pack(side=tk.LEFT, fill=tk.X, expand=True)

    def select_output_folder():
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            entry_out.delete(0, tk.END)
            entry_out.insert(0, folder)

    btn_browse_out = tk.Button(output_entry_frame, text="Browse", command=select_output_folder,
                               bg="#3498db", fg="white", font=("Arial", 10))
    btn_browse_out.pack(side=tk.RIGHT, padx=(5, 0))

    # Status and results section
    results_frame = tk.Frame(main_frame, bg="white", relief=tk.RAISED, bd=1)
    results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
    
    tk.Label(results_frame, text="📊 Status & Results:", 
             font=("Arial", 11, "bold"), bg="white").pack(pady=(10, 5), anchor=tk.W, padx=10)

    # Status text area
    status_text = scrolledtext.ScrolledText(results_frame, height=15, font=("Consolas", 10),
                                           bg="#2c3e50", fg="#ecf0f1", insertbackground="white")
    status_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
    
    def update_status(message):
        status_text.insert(tk.END, f"{message}\n")
        status_text.see(tk.END)
        root.update_idletasks()

    # Control buttons frame
    button_frame = tk.Frame(main_frame, bg="#f0f0f0")
    button_frame.pack(fill=tk.X)

    def process_file():
        # First validate Google Sheets URL
        sheets_url = entry_sheets.get().strip()
        if not sheets_url:
            messagebox.showerror("Error", "Please provide a Google Sheets URL or Sheet ID.")
            return
            
        sheet_id = extract_sheet_id(sheets_url)
        if not sheet_id:
            messagebox.showerror("Error", "Could not extract Sheet ID from the provided URL.\nPlease provide a correct full Google Sheets link or Sheet ID.")
            return
            
        # Generate URLs with the extracted sheet ID
        google_sheet_urls = [
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv",
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv",
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
        ]
        
        input_file = entry_file.get().strip()
        output_folder = entry_out.get().strip() or (os.path.dirname(input_file) if input_file else "")

        if not input_file:
            messagebox.showerror("Error", "Please select a file first.")
            return

        if not os.path.exists(input_file):
            messagebox.showerror("Error", "Selected file does not exist.")
            return

        # Clear previous results
        status_text.delete(1.0, tk.END)
        
        # Disable run button and change text
        btn_run.config(state=tk.DISABLED, text="🔄 Running...", bg="#95a5a6")
        btn_browse.config(state=tk.DISABLED)
        btn_browse_out.config(state=tk.DISABLED)
        
        def run_process():
            try:
                update_status("🚀 Starting blacklist check process...")
                update_status(f"🌐 Using Google Sheet ID: {sheet_id}")
                update_status(f"📁 Input file: {os.path.basename(input_file)}")
                update_status(f"📂 Output folder: {output_folder}")
                update_status("-" * 50)
                
                matches, cleaned_path, removed_path = check_blacklist(
                    input_file, google_sheet_urls, output_folder, update_status
                )
                
                update_status("-" * 50)
                update_status("🎉 PROCESS COMPLETED SUCCESSFULLY!")
                update_status(f"📊 Total matches found: {matches}")
                update_status(f"📄 Cleaned file saved: {os.path.basename(cleaned_path)}")
                update_status(f"📄 Removed numbers file: {os.path.basename(removed_path)}")
                update_status("-" * 50)
                
                if matches > 0:
                    update_status(f"⚠️  {matches} phone numbers were removed from your dataset")
                    update_status("💡 Check the 'removed' file to see which numbers were filtered out")
                else:
                    update_status("✅ No blacklisted numbers found - your dataset is clean!")
                    
            except Exception as e:
                update_status(f"❌ ERROR OCCURRED: {str(e)}")
                messagebox.showerror("Error", f"An error occurred:\n{str(e)}")
            finally:
                # Re-enable buttons
                btn_run.config(state=tk.NORMAL, text="🚀 Run Blacklist Check", bg="#27ae60")
                btn_browse.config(state=tk.NORMAL)
                btn_browse_out.config(state=tk.NORMAL)

        # Run in separate thread to prevent UI freezing
        thread = threading.Thread(target=run_process)
        thread.daemon = True
        thread.start()

    btn_run = tk.Button(button_frame, text="🚀 Run Blacklist Check", command=process_file,
                       bg="#27ae60", fg="white", font=("Arial", 12, "bold"), 
                       height=2, cursor="hand2")
    btn_run.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

    btn_exit = tk.Button(button_frame, text="❌ Exit", command=root.quit,
                        bg="#e74c3c", fg="white", font=("Arial", 12, "bold"), 
                        height=2, cursor="hand2")
    btn_exit.pack(side=tk.RIGHT, padx=(5, 0))

    # Initial welcome message
    welcome_msg = """Welcome to the Blacklist Phone Number Cleaner! 🧹

Instructions:
1. Provide the Google Sheets link to your blacklist (must be shared)
2. Select your Excel or CSV file containing phone numbers
3. (Optional) Choose an output folder - defaults to input file location  
4. Click 'Run Blacklist Check' to start processing
5. Results will appear here with detailed status updates

The program will:
✅ Load your phone numbers (smart column detection)
✅ Download the latest blacklist from your Google Sheets
✅ Compare and identify matches
✅ Create two output files:
   - *_cleaned.xlsx (numbers NOT on blacklist)  
   - *_removed.xlsx (numbers that WERE on blacklist)

Ready to clean your phone list! 📞✨
"""
    
    status_text.insert(tk.END, welcome_msg)

    root.mainloop()


if __name__ == "__main__":
    run_app()