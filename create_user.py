import csv
import requests
import logging
import re
import argparse

def setup_logging():
    """
    Function to set up logging for different log levels: ERROR, WARNING, and INFO.
    Logs errors to 'error_log.txt', warnings to 'warning_log.txt', and info messages to 'info_log.txt'.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Set the minimum logging level to DEBUG
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    def create_handler(filename, level, filter_func=None):
        # Function to create and configure a log handler, Filters logs based on the specified level.
        handler = logging.FileHandler(filename)
        handler.setLevel(level)
        handler.setFormatter(formatter)
        if filter_func:
            f = logging.Filter()
            f.filter = filter_func
            handler.addFilter(f)
        logger.addHandler(handler)
        return handler

    # Create log files for different severity levels
    create_handler('error_log.txt', logging.ERROR, lambda record: record.levelno >= logging.ERROR)
    create_handler('warning_log.txt', logging.WARNING, lambda record: logging.WARNING <= record.levelno < logging.ERROR)
    create_handler('info_log.txt', logging.INFO, lambda record: record.levelno == logging.INFO)

# Logging functions to log msgs at different severity levels
def log_error(msg):
    logging.error(msg)  # Logs an error message

def log_warning(msg):
    logging.warning(msg)    # Logs an warning message

def log_info(msg):
    logging.info(msg)   # Logs an info message

def create_users(row, max_retries=3):
    """
    Attempts to create a user by making a POST request to an API.
    Retries up to 'max_retries' times in case of failure.
    Logs success, failure, or request exceptions.
    """
    print(f"Attempting to create user: {row}")
    retries = 0 # Initialize retry counter

    # Retry loop in case of failure
    while max_retries > retries:
        try:
            response = requests.post("http://localhost:5000/api/create_user", json=row)  # Send a POST request with user data
            print(f"Response Status Code: {response.status_code}")  # Print the HTTP status code

            if response.status_code == 201:  # Check if the request was successful (201 Created)
                log_info(f"User created successfully (Status {response.status_code}): {row}")  # Log success message
                return  # Exit the function if user creation is successful
            else:
                log_error(f"Failed to create user (Status {response.status_code}): {row}")  # Log error if creation fails
        except requests.exceptions.RequestException as e: 
            log_error(f"Failed to create user {row}: {e}")  # Log API request failure
        
        retries += 1  # Increment retry counter

    log_error(f"Failed to create user {row} after {max_retries} attempts.")  # Log final failure after retrying

def validate_row(row, required_fields):
    """
    Validates a row from the CSV file before processing
    - Checks if required fields are present
    - Validates email format
    - Assigns default values if needed
    - Returns True if validation fails to skip the row, False otherwise
    """
    email_pattern = r"[^@]+@[^@]+\.[^@]+"  # Email validation regex

    for field in required_fields:
        if not row.get(field):
            log_warning(f"Skipping row due to missing required field: {field} in {row}")
            return True # Return True to skip the row 

    if 'email' in row and re.match(email_pattern, row.get('email', '')) is None:    # validate email format
        log_warning(f"Skipping row due to invalid email address: {row}")
        return True  # Return True to skip invalid email rows

    # Extract name from email if the name is missing
    if 'email' in row and row['email']:
        row['name'] = row.get('name') or row['email'].split('@')[0].capitalize()    # Extract name from email and capitalize it

    # Assign default role as user
    if 'role' in row and row['role'] == '':
        row['role'] = 'user'    # if role is empty (name,email,)
    elif 'role' not in row:
        row['role'] = 'user'    # if role is missing (name,email)

    print(f"Processing row: {row}")

def read_csv(file_path, fields, required_fields):
    """
    Reads a CSV file and processes each row.
    - Validates headers.
    - Checks for missing or invalid data.
    - Calls 'create_users' for valid rows.
    """
    try:
        with open(file_path, 'r') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:   # Check if the file has headers
                log_error("The CSV file is empty or missing headers.")
                return
            
            # Check the CSV file has all expected headers
            for field in fields:
                if field not in reader.fieldnames:
                    log_error(f"Missing expected columns in the CSV. Expected: {fields}, Available: {reader.fieldnames}")
                    return

            # Process each row in the CSV
            for row in reader:
                if validate_row(row, required_fields):
                    continue  # Skip invalid rows
                create_users(row)  # Create user for valid rows

    except FileNotFoundError:
        log_error(f"The file '{file_path}' was not found.")  # Log file not found error
    except csv.Error as e:
        log_error(f"CSV error while reading the file: {e}")  # Log CSV parsing errors
    except Exception as e:
        log_error(f"Unexpected error: {e}")  # Catch and log any other exceptions

def main():
    """
    Main function :
    - Parses command-line arguments.
    - Sets up logging.
    - Calls 'read_csv' with CSV file, fields, required fields.
    """
    parser = argparse.ArgumentParser(description="User creation script")
    parser.add_argument('csv_file', type=str, help="Path to the CSV file containing user data")
    args = parser.parse_args()

    setup_logging()  # Initialize logging

    fields = ['name','email','role']  # List of expected CSV columns
    required_fields = ['email']  # List of required fields

    read_csv(args.csv_file, fields, required_fields)  # Starts reading CSV

if __name__ == "__main__":
    main()  # Run the script