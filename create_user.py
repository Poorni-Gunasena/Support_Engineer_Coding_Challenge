import csv
import requests
import logging
import re
import argparse

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    def create_handler(filename, level, filter_func=None):
        handler = logging.FileHandler(filename)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        if filter_func:
            f = logging.Filter()
            f.filter = filter_func
            handler.addFilter(f)
        logger.addHandler(handler)
        return handler

    create_handler('error_log.txt', logging.ERROR, lambda record: record.levelno >= logging.ERROR)
    create_handler('warning_log.txt', logging.WARNING, lambda record: logging.WARNING <= record.levelno < logging.ERROR)
    create_handler('info_log.txt', logging.INFO, lambda record: record.levelno == logging.INFO)

def log_error(msg):
    logging.error(msg)

def log_warning(msg):
    logging.warning(msg)

def log_info(msg):
    logging.info(msg)

def create_users(row, max_retries=3):
    print(f"Attempting to create user: {row}")
    retries = 0
    while max_retries > retries:
        try:
            response = requests.post("http://localhost:5000/api/create_user", json=row)
            print(f"Response Status Code: {response.status_code}")
            if response.status_code == 201:
                log_info(f"User created successfully (Status {response.status_code}): {row}")
                return
            else:
                log_error(f"Failed to create user (Status {response.status_code}): {row}")
        except requests.exceptions.RequestException as e:
            log_error(f"Failed to create user {row}: {e}")
        
        retries += 1
    
    log_error(f"Failed to create user {row} after {max_retries} attempts.")

def validate_row(row, required_fields):
    email_pattern = r"[^@]+@[^@]+\.[^@]+"

    missing_required = False
    for field in required_fields:
        if not row.get(field):
            log_warning(f"Skipping row due to missing required field: {field} in {row}")
            missing_required = True
            break  

    if missing_required:
        return missing_required  

    if 'email' in row and re.match(email_pattern, row.get('email', '')) is None:
        log_warning(f"Skipping row due to invalid email address: {row}")
        return True 

    if 'email' in row and row['email']:
        row['name'] = row.get('name') or row['email'].split('@')[0].capitalize()
        
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
    parser = argparse.ArgumentParser(description="User creation script")
    parser.add_argument('csv_file', type=str, help="Path to the CSV file containing user data")

    args = parser.parse_args()
    setup_logging()

    fields = ['name','email','role']
    required_fields = ['email']
    read_csv(args.csv_file, fields, required_fields)

if __name__ == "__main__":
    main()