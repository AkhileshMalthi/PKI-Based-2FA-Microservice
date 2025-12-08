# FastAPI Web Server 

from fastapi import FastAPI, HTTPException, Response, status
from pydantic import BaseModel
import os
import sys

# Import our custom logic
from app.crypto_utils import decrypt_seed, load_private_key
from app.totp_utils import generate_totp_code, verify_totp_code, get_remaining_seconds
from dotenv import load_dotenv

load_dotenv()


app = FastAPI(title="Secure 2FA Microservice")

# --- CONFIGURATION ---
# The path where Docker mounts the volume.
# CRITICAL: This must match the volume in docker-compose.yml
DATA_DIR = os.getenv("DATA_DIR", "/data")
SEED_FILE = os.getenv("SEED_FILE", os.path.join(DATA_DIR, "seed.txt"))
PRIVATE_KEY_FILE = os.getenv("PRIVATE_KEY_FILE", "student_private.pem")

# --- PYDANTIC MODELS (Input Validation) ---
class DecryptRequest(BaseModel):
    encrypted_seed: str

class VerifyRequest(BaseModel):
    code: str

# --- HELPER ---
def get_seed():
    """Reads the seed from disk. Raises error if not found."""
    if not os.path.exists(SEED_FILE):
        raise FileNotFoundError("Seed not found")
    with open(SEED_FILE, "r") as f:
        return f.read().strip()

# --- ENDPOINTS ---

@app.post("/decrypt-seed")
async def decrypt_seed_endpoint(request: DecryptRequest, response: Response):
    """
    Step 1: Receive encrypted seed -> Decrypt -> Save to /data/seed.txt
    """
    try:
        # 1. Load Private Key
        if not os.path.exists(PRIVATE_KEY_FILE):
             # Try absolute path for Docker container
             # In Docker, we usually copy it to /app/student_private.pem
             if os.path.exists("/app/student_private.pem"):
                 key_path = "/app/student_private.pem"
             else:
                 print("CRITICAL: Private key not found!")
                 raise Exception("Private key not found")
        else:
            key_path = PRIVATE_KEY_FILE

        private_key = load_private_key(key_path)

        # 2. Decrypt the seed
        # This uses your logic from crypto_utils.py
        decrypted_hex = decrypt_seed(request.encrypted_seed, private_key)

        # 3. Save to Persistent Storage
        # Ensure directory exists (just in case)
        os.makedirs(DATA_DIR, exist_ok=True)
        
        with open(SEED_FILE, "w") as f:
            f.write(decrypted_hex)
            
        return {"status": "ok"}

    except Exception as e:
        # Log the error for debugging
        print(f"Decryption failed: {str(e)}", file=sys.stderr)
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "Decryption failed"}

@app.get("/generate-2fa")
async def generate_2fa(response: Response):
    """
    Step 2: Read seed -> Generate Code
    """
    try:
        hex_seed = get_seed()
        
        code = generate_totp_code(hex_seed)
        remaining = get_remaining_seconds()
        
        return {
            "code": code,
            "valid_for": remaining
        }
    except FileNotFoundError:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "Seed not decrypted yet"}
    except Exception as e:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": str(e)}

@app.post("/verify-2fa")
async def verify_2fa(request: VerifyRequest, response: Response):
    """
    Step 3: Verify user code against stored seed
    """
    if not request.code:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return {"error": "Missing code"}
        
    try:
        hex_seed = get_seed()
        
        # Verify with ±1 period tolerance (30 seconds)
        is_valid = verify_totp_code(hex_seed, request.code, valid_window=1)
        
        return {"valid": is_valid}

    except FileNotFoundError:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "Seed not decrypted yet"}
    except Exception as e:
        print(f"Verification error: {str(e)}")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return {"error": "Internal processing error"}