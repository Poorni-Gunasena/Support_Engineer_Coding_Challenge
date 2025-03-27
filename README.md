# Create User Account 

## Overview  
This script automates the process of reading user data from a CSV file, validating it, and sending API requests to create users in a system. It includes error handling, logging, and retry mechanisms to ensure smooth execution.

## Changes have been made

### 1. Improved Logging   
- **Errors** → `error_log.txt`  
- **Warnings** → `warning_log.txt`  
- **Information** → `info_log.txt`  

### 2. CSV Header Validation
The script checks if the CSV file contains the expected headers:

```csv
name,email,role
```
- If any expected columns are missing, an error is logged, and the script stops processing.
- If the CSV file is empty or does not have headers, an error is logged.

### 3. Data Validation  
- Ensures required fields (`email`) are present.  
- Validates email format.
- If required field missing or email format is invalid it skips the row.  
- If `name` is missing, it extracts it from the email (e.g., `alice@example.com` → `Alice`).  
- If `role` is missing, it defaults to `"user"`.  

### 4. Automatic Retries for API Calls  
- If user creation fails, the script retries **up to 3 times** before logging an error.  

## Run the Script 

Execute the following command, passing the path to your CSV file as an argument:

```sh
python create_user.py csv_file.csv
```

For example, if the CSV file is named users.csv, run:

```sh
python create_user.py users.csv
```
