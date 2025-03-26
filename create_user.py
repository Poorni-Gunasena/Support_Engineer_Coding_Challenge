import csv
import requests

def create_users(file_path):
    with open(file_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            response = requests.post("https://example.com/api/create_user", json=row)
            if response.status_code != 201:
                print("Error creating user:", row["email"])

create_users("users.csv")
