import time
from app.totp_utils import generate_totp_code, verify_totp_code

def test():
    # 1. Use a fake hex seed (must be 64 chars)
    # This acts like the "Decrypted Seed" we will get later
    fake_seed = "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef"
    
    print(f"Testing with Fake Seed: {fake_seed[:10]}...")

    # 2. Generate a code
    code = generate_totp_code(fake_seed)
    print(f"Generated Code: {code}")

    # 3. Verify it immediately (Should be True)
    is_valid = verify_totp_code(fake_seed, code)
    print(f"Immediate Verification: {'✅ PASS' if is_valid else '❌ FAIL'}")

    # 4. Verify a wrong code (Should be False)
    is_valid_wrong = verify_totp_code(fake_seed, "000000")
    print(f"Wrong Code Verification: {'✅ PASS' if not is_valid_wrong else '❌ FAIL'}")

if __name__ == "__main__":
    test()