# TOTP generation logic

import pyotp
import base64
import time

def generate_totp_code(hex_seed: str) -> str:
    """
    Generate current TOTP code from hex seed.
    
    Args:
        hex_seed: 64-character hex string
    
    Returns:
        6-digit TOTP code as string
    """
    # 1. Convert HEX to BYTES
    seed_bytes = bytes.fromhex(hex_seed)
    
    # 2. Convert BYTES to BASE32
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
    
    # 3. Create TOTP object
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30, digest='sha1')
    
    # 4. Generate current code
    return totp.now()

def verify_totp_code(hex_seed: str, code: str, valid_window: int = 1) -> bool:
    """
    Verify TOTP code with time window tolerance.
    
    Args:
        valid_window: 1 means we accept codes from ±30 seconds ago/future.
    """
    # 1. Convert to Base32 (Same as above)
    seed_bytes = bytes.fromhex(hex_seed)
    base32_seed = base64.b32encode(seed_bytes).decode('utf-8')
    
    # 2. Create TOTP object
    totp = pyotp.TOTP(base32_seed, digits=6, interval=30, digest='sha1')
    
    # 3. Verify
    # This checks the current time AND the window (±30s) automatically.
    return totp.verify(code, valid_window=valid_window)

def get_remaining_seconds() -> int:
    """
    Helper to calculate how many seconds are left in the current 30s window.
    Used for the /generate-2fa response.
    """
    return 30 - (int(time.time()) % 30)