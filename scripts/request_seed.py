import os

def request_seed(student_id: str, github_repo_url: str, api_url: str):
    """
    Request encrypted seed from instructor API
    
    Steps:
    1. Read student public key from PEM file
       - Open and read the public key file
       - Keep the PEM format with BEGIN/END markers
    
    2. Prepare HTTP POST request payload
       - Create JSON with student_id, github_repo_url, public_key
       - Most HTTP libraries handle newlines in JSON automatically
    
    3. Send POST request to instructor API
       - Use your language's HTTP client
       - Set Content-Type: application/json
       - Include timeout handling
    
    4. Parse JSON response
       - Extract 'encrypted_seed' field
       - Handle error responses appropriately
    
    5. Save encrypted seed to file
       - Write to encrypted_seed.txt as plain text
    """
    
    import json
    import requests

    # Step 1: Read student public key from PEM file
    try:
        with open("student_public.pem", "r") as f:
            public_key_pem = f.read()
    except FileNotFoundError:
        print("Error: student_public.pem file not found.")
        return

    # Step 2: Prepare HTTP POST request payload
    payload = {
        "student_id": student_id,
        "github_repo_url": github_repo_url,
        "public_key": public_key_pem,
    }
    headers = {"Content-Type": "application/json"}

    # Step 3: Send POST request to instructor API
    try:
        response = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error during API request: {e}")
        return

    # Step 4: Parse JSON response
    try:
        response_data = response.json()
        encrypted_seed = response_data["encrypted_seed"]
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing API response: {e}")
        return

    # Step 5: Save encrypted seed to file
    with open("encrypted_seed.txt", "w") as f:
        f.write(encrypted_seed)

    print("Encrypted seed saved to 'encrypted_seed.txt'")

if __name__ == "__main__":
    # Example usage
    from dotenv import load_dotenv
    
    load_dotenv()
    
    STUDENT_ID = os.getenv("STUDENT_ID", "your_student_id")
    GITHUB_REPO_URL = os.getenv("GITHUB_REPO_URL", "your_github_repo_url")
    INSTRUCTOR_URL = os.getenv("INSTRUCTOR_URL", "your_instructor_url")

    request_seed(STUDENT_ID, GITHUB_REPO_URL, INSTRUCTOR_URL)