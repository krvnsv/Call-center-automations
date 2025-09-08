# Python automation scripts for bulk phone calls

CLI micro apps I developed while working as a truck driver recruiter instead of doing any actual work.

## Black list checker

The latest version (google_sheets_blacklist_checker.py) takes a .xlsx file containing phone numbers and compares it against the latest version of Blacklist which it pulls from the Google Sheets.
 
All blacklisted numbers are thrown away, and a clean downloadable list of phone numbers is produced saving a ton of time.

## Phone number copy paste

Automatically copies a phone number from the preselected .csv list of numbers for the day. Once the copied number is pasted, copies the next one. In case user needs to copy something else and presses ctrl+c, saves the state and halts the program. 

Provides call history in a separrate window. Makes the workflow more efficient and smooth while also saving some time.
