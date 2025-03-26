import csv
import requests
import logging
import re

def setup_logging():
    logging.basicConfig(filename='error_log.txt', level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

def log_error(msg):
    logging.error(msg)

def create_users(row):
    print(f"Attempting to create user: {row}")
    try:
        response = requests.post("http://localhost:5000/api/create_user", json=row)
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Content: {response.text}")
        if response.status_code != 201:
            log_error(f"Failed to create user (Status {response.status_code}): {row}")
    except requests.exceptions.RequestException as e:
        log_error(f"Failed to create user {row}: {e}")

def validate_row(row, required_fields):
    email_pattern = r"[^@]+@[^@]+\.[^@]+"

    missing_required = False
    for field in required_fields:
        if not row.get(field):
            log_error(f"Skipping row due to missing required field: {field} in {row}")
            missing_required = True
            break  

    if missing_required:
        return missing_required  

    if 'email' in row and re.match(email_pattern, row.get('email', '')) is None:
        log_error(f"Skipping row due to invalid email address: {row}")
        return True 

    print(f"Processing row: {row}")
    if 'role' in row and row['role'] == '':
        row['role'] = 'user'
    elif 'role' not in row:
        row['role'] = 'user' 

def read_csv(file_path, fields, required_fields):
    try:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                log_error("The CSV file is empty or missing headers.")
                return
            
            missing_header = False
            for field in fields:
                if field not in reader.fieldnames:
                    missing_header = True
                    break

            if missing_header:
                log_error(f"Missing expected columns in the CSV. Expected: {fields}, Available: {reader.fieldnames}")
                return

            for row in reader:
                if validate_row(row, required_fields):
                    continue
                create_users(row)

    except FileNotFoundError:
        log_error(f"The file '{file_path}' was not found.")
    except csv.Error as e:
        log_error(f"CSV error while reading the file: {e}")
    except Exception as e:
        log_error(f"Unexpected error: {e}")

def main():
    setup_logging()

    fields = ['name','email','role']
    required_fields = ['email']
    read_csv("users.csv", fields, required_fields)

if __name__ == "__main__":
    main()