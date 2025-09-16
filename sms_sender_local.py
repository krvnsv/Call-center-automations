"""
Simplified bulk SMS sender using pyautogui.
Procedure:
1. Copy number
2. Click New Text button
3. Paste (Ctrl+V) → Enter
4. Copy message
5. Click opt-out dismissal → Click Next button
6. Paste (Ctrl+V) → Enter
7. Repeat for all numbers
Numbers loaded from sms_numbers.csv (first column)
Marks numbers as messaged in CSV to avoid duplicates
"""

import time
import random
import logging
import pyautogui
import pyperclip
import csv
from pathlib import Path

# Safety
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.25

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# === CONFIG ===
ITERATIONS = 100                # max messages to send
START_DELAY = 5                 # seconds before starting
TEST_RUNS = 2                   # test sends first

# Coordinates
COORDS = {
    "new_text_button": (332, 139),
    "next_button": (631, 551),
    "opt_out_dismiss": (95, 494),
}

# === MESSAGE ===
msg_1 = """Hi,
This is Ray im an Independent recruiter with more than 3 years of experience in industry.
Currently hiring Lease to Purchase CDL-A drivers (SAP friendly).
- Drive in any of the 48 states you choose
- No forced dispatch
- Pick your loads & home time
- 75% of the load revenue
- Only 6+ months OTR of experience required
- Orientation in Chicago or Jacksonville, FL
I work with a couple of different companies so Company positions, Owners, Box truck are also an option.
If Interested -
Send the following to apply:
- CDL A (both sides)
- Medical card
- Clearinghouse screenshot
Check out the website: https://janda-transportation.com/
Thanks! – Ray Stinson
"""

msg_2 = """Hi,
This is Ray - Independent recruiter with more than 3 years of experience in industry.
J&A Logistics is hiring Lease to Purchase CDL-A drivers (SAP friendly).
- Choose any of the 48 states you want to drive in
- No forced dispatch
- Pick your loads & home time
- 75% of the load revenue
- Only 6+ months OTR of experience required
- Orientation in Chicago or Jacksonville, FL
I also work with a few other companies, so Company positions, Owner-operators, and Box trucks are options.
If Interested -
Send the following to apply:
- CDL A (both sides)
- Medical card
- Clearinghouse screenshot
Check out the website: https://janda-transportation.com/
Thanks! – Ray Stinson
"""

msg_3 = """Hi,
This is Ray - Independent recruiter with over 3 years of experience in the industry.
J&A Logistics is looking for Lease to Purchase CDL-A drivers (SAP friendly, partner & pet friendly).
- Drive in any states you prefer out of the 48
- No forced dispatch
- Pick your loads & home time
- 75% of the load revenue
- Minimum 6 months OTR experience required
- Orientation in Chicago or Jacksonville, FL
I also partner with other companies, so Company positions, Owner-operators, and Box trucks are available.
If Interested -
Send the following to apply:
- CDL A (both sides)
- Medical card
- Clearinghouse screenshot
Check out the website: https://janda-transportation.com/
Thanks! – Ray Stinson
"""

msg_4 = """Hi,
This is Ray - Independent recruiter with more than 3 years of experience in industry.
J&A Logistics is hiring Lease to Purchase CDL-A drivers (SAP friendly).
- Choose any of the 48 states you want to drive in
- No forced dispatch
- Pick your loads & home time
- 75% of the load revenue
- Loadboard available for easy scheduling
- Only 6+ months OTR of experience required
- Orientation in Chicago or Jacksonville, FL
We work with multiple companies, so Company positions, Owner-operators, and Box trucks (used & brand new) are also options.
If Interested
Send the following to apply:
- CDL A (both sides)
- Medical card
- Clearinghouse screenshot
Or apply here: https://docs.google.com/forms/d/e/1FAIpQLSe4XcUtWgg3IMF1D5acznad6C8WlBkke4LJr2TvdUuHAYMYEA/viewform
Thanks! – Ray Stinson
"""

msg_5 = """Hi,
This is Ray - Independent recruiter with over 3 years in the trucking industry.
Currently hiring Lease to Purchase CDL-A drivers (SAP friendly, team & partner friendly).
- Drive in any states you prefer out of the 48
- No forced dispatch
- Pick your loads & home time
- 75% of the load revenue
- Orientation in Chicago or Jacksonville, FL
- Loadboard available and ready to use
We also offer Company positions, Owner-operators, and Box trucks (used & brand new) through other partner companies.
If Interested-
Send the following to apply:
- CDL A (both sides)
- Medical card
- Clearinghouse screenshot
Or apply here: https://docs.google.com/forms/d/e/1FAIpQLSe4XcUtWgg3IMF1D5acznad6C8WlBkke4LJr2TvdUuHAYMYEA/viewform
Thanks! – Ray Stinson
"""

def get_random_message():
    messages = [msg_1, msg_2, msg_3, msg_4, msg_5]
    idx = random.randrange(len(messages))
    return idx + 1, messages[idx]   # returns (message number, message text)


MESSAGE = get_random_message()

# === LOAD NUMBERS ===
def load_numbers(file_path="sms_numbers.csv"):
    path = Path(file_path)
    if not path.exists():
        logging.error("Numbers file %s not found.", file_path)
        return []

    numbers = []
    rows = []

    with open(path, newline='', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            rows.append(row)
            if not row:
                continue
            num = row[0].strip()
            # Skip already messaged numbers
            if len(row) > 1 and row[1].lower() == "messaged":
                continue
            numbers.append((num, row))
    return numbers, rows

def mark_number_messaged(file_path, row_to_mark):
    path = Path(file_path)
    all_rows = []
    with open(path, newline='', encoding="utf-8") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            all_rows.append(row)

    for row in all_rows:
        if row[0].strip() == row_to_mark[0].strip():
            if len(row) == 1:
                row.append("messaged")
            elif len(row) > 1:
                row[1] = "messaged"

    with open(path, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(all_rows)

# === HELPERS ===
def paste_text(text):
    pyperclip.copy(text)
    time.sleep(0.2)  # short pause to ensure clipboard is ready
    pyautogui.keyDown('ctrl')
    pyautogui.press('v')
    pyautogui.keyUp('ctrl')
    time.sleep(0.3)  # wait for paste to register

def send_one(number, message):
    # 1. Click New Text
    pyautogui.click(*COORDS['new_text_button'])
    time.sleep(random.uniform(0.5, 1.0))

    # 2. Paste number → Enter
    paste_text(number)
    time.sleep(random.uniform(0.5, 1.0))  # let UI register number
    pyautogui.press('enter')
    time.sleep(random.uniform(0.3, 0.6))

    # 3. Dismiss opt-out message
    pyautogui.click(*COORDS['opt_out_dismiss'])
    time.sleep(random.uniform(0.3, 0.5))

    # 4. Click Next button
    pyautogui.click(*COORDS['next_button'])
    time.sleep(0.5)  # wait for message field to get focus

    # 5. Paste message → Enter
    paste_text(message)
    pyautogui.press('enter')
    time.sleep(random.uniform(1.0, 2.0))  # polite delay between sends

# === MAIN ===
def main():
    numbers, _ = load_numbers("sms_numbers.csv")
    if not numbers:
        logging.error("No numbers found to send, exiting.")
        return

    total = min(ITERATIONS, len(numbers))
    logging.info("Loaded %d numbers. Will attempt %d sends.", len(numbers), total)

    # === PRE-RUN CHECKS ===
    input("Is RingCentral opened in the correct location? Press Enter to continue...")
    input("Is the Text tab active? Press Enter to continue...")

    logging.info("Starting in %d seconds...", START_DELAY)
    time.sleep(START_DELAY)

    # Test runs
    runs = min(TEST_RUNS, total)
    logging.info("Running %d test sends first.", runs)
    for i in range(runs):
        num, row = numbers[i]
        msg_index, message = get_random_message()  # correct unpacking
        logging.info("Test run %d/%d , message #%d -> %s", i+1, runs, msg_index, num)
        send_one(num, message)
        mark_number_messaged("sms_numbers.csv", row)

    input("If test looked correct, press Enter to continue with the remaining sends (or Ctrl+C to abort)...")

    # Full run
    for i in range(runs, total):
        try:
            num, row = numbers[i]
            msg_index, message = get_random_message()  # correct unpacking
            logging.info("Full run %d/%d , message #%d -> %s", i+1, total, msg_index, num)
            send_one(num, message)
            mark_number_messaged("sms_numbers.csv", row)
            time.sleep(random.uniform(2.0, 6.0))
        except KeyboardInterrupt:
            logging.warning("Interrupted by user. Exiting.")
            break
        except Exception as e:
            logging.exception("Error on iteration %d: %s — continuing to next", i+1, e)
            time.sleep(5)

    logging.info("Done.")




if __name__ == "__main__":
    main()
