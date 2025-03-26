import csv
import requests

def create_users(file_path):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            print(f"Attempting to create user: {row}")
            try:
                response = requests.post("http://localhost:5000/api/create_user", json=row)
                print(f"Response Status Code: {response.status_code}")
                print(f"Response Content: {response.text}")
                if response.status_code != 201:
                    print(f"Error creating user (Status {response.status_code}): {row['email']}")
            except requests.exceptions.RequestException as e:
                print(f"Error creating user {row['email']}: {e}")

create_users("users.csv")