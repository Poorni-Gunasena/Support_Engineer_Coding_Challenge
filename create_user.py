import csv
import requests
import logging

def setup_logging():
    logging.basicConfig(filename='error_log.txt', level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

def log_error(msg):
    logging.error(msg)

def create_users(file_path):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row['email'] == '':
                continue
            
            print(f"Attempting to create user: {row}")
            try:
                response = requests.post("http://localhost:5000/api/create_user", json=row)
                print(f"Response Status Code: {response.status_code}")
                print(f"Response Content: {response.text}")
                if response.status_code != 201:
                    log_error(f"Failed to create user (Status {response.status_code}): {row}")
            except requests.exceptions.RequestException as e:
                log_error(f"Failed to create user {row}: {e}")

def main():
    setup_logging()
    create_users("users.csv")

if __name__ == "__main__":
    main()