import csv
import pyperclip
import keyboard
import time
import os
import sys

# ---------- CONFIG ----------
CSV_FILE = "phone_numbers.csv"  # Default CSV file name
PASTE_HOTKEY = "ctrl+v"         # Hotkey to detect pasting
QUIT_HOTKEY = "ctrl+c"          # Hotkey to quit program

def load_numbers(csv_file):
    """Load phone numbers from CSV file."""
    numbers = []
    
    if not os.path.exists(csv_file):
        print(f"❌ Error: {csv_file} not found.")
        return None
    
    try:
        with open(csv_file, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) == 0:
                    continue  # Skip empty rows
                elif len(row) == 1:
                    # Only phone number, add empty status column
                    if row[0].strip():  # Only add non-empty phone numbers
                        numbers.append([row[0].strip(), ""])
                else:
                    # Phone number and status
                    if row[0].strip():  # Only add non-empty phone numbers
                        numbers.append([row[0].strip(), row[1].strip()])
        
        print(f"✅ Loaded {len(numbers)} phone numbers from '{csv_file}'")
        return numbers
        
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return None

def save_numbers(csv_file, numbers):
    """Save phone numbers back to CSV file."""
    try:
        with open(csv_file, "w", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(numbers)
        return True
    except Exception as e:
        print(f"❌ Error saving CSV file: {e}")
        return False

def find_next_uncalled(numbers, start_index=0):
    """Find the next uncalled phone number starting from start_index."""
    for i in range(start_index, len(numbers)):
        if numbers[i][1].strip().lower() != "called":
            return i
    return None

def main():
    """Main function to run the phone number automator."""
    print("🚀 Phone Number Automation Tool")
    print("=" * 40)
    
    # Get CSV file path from user
    csv_file = input("Enter CSV file path (or press Enter for 'phone_numbers.csv'): ").strip()
    if not csv_file:
        csv_file = CSV_FILE
    
    # Load numbers from CSV
    numbers = load_numbers(csv_file)
    if numbers is None:
        return
    
    if len(numbers) == 0:
        print("❌ No phone numbers found in the file.")
        return
    
    # Display summary
    total_numbers = len(numbers)
    called_numbers = sum(1 for row in numbers if row[1].strip().lower() == "called")
    remaining_numbers = total_numbers - called_numbers
    
    print(f"📊 Summary:")
    print(f"   Total numbers: {total_numbers}")
    print(f"   Already called: {called_numbers}")
    print(f"   Remaining: {remaining_numbers}")
    print()
    
    # Find first uncalled number
    index = find_next_uncalled(numbers)
    if index is None:
        print("🎉 All numbers already marked as called!")
        return
    
    # Copy first number to clipboard
    try:
        pyperclip.copy(numbers[index][0])
        print(f"📋 First number copied to clipboard: {numbers[index][0]}")
    except Exception as e:
        print(f"❌ Error copying to clipboard: {e}")
        return
    
    print("\n📝 Instructions:")
    print("   • Paste the number anywhere using Ctrl+V")
    print("   • Program will automatically verify and move to next number")
    print("   • Press Ctrl+C to stop the program")
    print("\n🎧 Listening for Ctrl+V presses...")
    
    # Flag to control the program
    running = True
    
    def on_quit():
        """Handle Ctrl+C to quit."""
        nonlocal running
        print("\n🛑 Program stopped by user (Ctrl+C detected)")
        running = False
    
    # Set up quit hotkey
    keyboard.add_hotkey(QUIT_HOTKEY, on_quit)
    
    # ---------- MAIN LOOP ----------
    while running and index is not None and index < len(numbers):
        try:
            # Wait for paste hotkey
            keyboard.wait(PASTE_HOTKEY)
            
            if not running:  # Check if user pressed Ctrl+C
                break
            
            # Small delay to ensure paste operation completes
            time.sleep(0.1)
            
            # Check clipboard content
            try:
                pasted = pyperclip.paste().strip()
                expected = numbers[index][0].strip()
                
                if pasted == expected:
                    print(f"✅ Verified paste: {expected}")
                    
                    # Mark as called
                    numbers[index][1] = "called"
                    
                    # Save CSV
                    if save_numbers(csv_file, numbers):
                        print(f"💾 Marked as called and saved to file")
                        print("\n----------\n")
                        
                        # Find next uncalled number
                        next_index = find_next_uncalled(numbers, index + 1)
                        
                        if next_index is not None:
                            index = next_index
                            pyperclip.copy(numbers[index][0])
                            print(f"📋 Next number copied: {numbers[index][0]}")
                        else:
                            print("🎉 All phone numbers have been processed!")
                            running = False
                            break
                    else:
                        print("❌ Failed to save to file. Continuing...")
                        
                else:
                    print(f"⚠️  WARNING: Pasted '{pasted}' but expected '{expected}'")
                    print("   Status not updated. Please paste the correct number.")
                
            except Exception as e:
                print(f"❌ Error checking clipboard: {e}")
            
            # Small delay to prevent double triggers
            time.sleep(0.2)
            
        except KeyboardInterrupt:
            print("\n🛑 Program stopped by user")
            break
        except Exception as e:
            print(f"❌ Error in main loop: {e}")
            time.sleep(1)
    
    print("\n✨ Program finished!")

if __name__ == "__main__":
    # Check if required libraries are installed
    try:
        import pyperclip
        import keyboard
    except ImportError as e:
        missing_libs = []
        if "pyperclip" in str(e):
            missing_libs.append("pyperclip")
        if "keyboard" in str(e):
            missing_libs.append("keyboard")
        
        if missing_libs:
            print(f"❌ Error: Missing required libraries: {', '.join(missing_libs)}")
            print(f"📦 Install them using: pip install {' '.join(missing_libs)}")
            sys.exit(1)
    
    main()