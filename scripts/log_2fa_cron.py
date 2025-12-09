import sys
import os
import datetime

# Add the parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.totp_utils import generate_totp_code
from dotenv import load_dotenv

load_dotenv()

SEED_FILE = os.getenv("SEED_FILE", "/data/seed.txt")

def run_cron():
    # 1. Check if seed exists
    if not os.path.exists(SEED_FILE):
        print(f"{datetime.datetime.now(datetime.timezone.utc)} - Error: Seed not found (System waiting for decryption)", file=sys.stderr)
        return

    try:
        # 2. Read Seed
        with open(SEED_FILE, "r") as f:
            hex_seed = f.read().strip()

        # 3. Generate Code
        code = generate_totp_code(hex_seed)

        # 4. Get UTC Timestamp
        # Requirement: Use UTC timezone for timestamps
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        timestamp = now_utc.strftime("%Y-%m-%d %H:%M:%S")

        # 5. Output Format: YYYY-MM-DD HH:MM:SS - 2FA Code: XXXXXX
        print(f"{timestamp} - 2FA Code: {code}")

    except Exception as e:
        print(f"Cron Error: {e}", file=sys.stderr)

if __name__ == "__main__":
    run_cron()