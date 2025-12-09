import subprocess
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa

# --- CONFIGURATION ---
STUDENT_PRIVATE_KEY = "student_private.pem"
INSTRUCTOR_PUBLIC_KEY = "instructor_public.pem"

def get_git_commit_hash() -> str:
    """
    Gets the latest git commit hash from the command line.
    """
    try:
        # Run git log -1 --format=%H
        commit_hash = subprocess.check_output(
            ["git", "log", "-1", "--format=%H"], 
            stderr=subprocess.STDOUT
        ).decode('utf-8').strip()
        
        # Validation: Hash must be 40 hex characters
        if len(commit_hash) != 40:
            raise ValueError(f"Invalid commit hash length: {len(commit_hash)}")
            
        return commit_hash
    except subprocess.CalledProcessError as e:
        print("❌ Error: Could not get git commit hash.")
        print("   Make sure you are in a git repository and have made at least one commit.")
        print(f"   Git Error: {e.output.decode()}")
        exit(1)

def load_keys():
    """
    Loads student private key and instructor public key.
    """
    print("Loading keys...")
    
    # 1. Load Student Private Key
    with open(STUDENT_PRIVATE_KEY, "rb") as f:
        student_key = serialization.load_pem_private_key(
            f.read(),
            password=None
        )

    # 2. Load Instructor Public Key
    with open(INSTRUCTOR_PUBLIC_KEY, "rb") as f:
        instructor_key = serialization.load_pem_public_key(
            f.read()
        )
        
    return student_key, instructor_key

def sign_message(message: str, private_key) -> bytes:
    """
    Sign the ASCII commit hash using RSA-PSS with SHA-256.
    """
    # CRITICAL: Encode string to bytes (ASCII/UTF-8)
    # The prompt explicitly warns NOT to convert hex-string to bytes.
    message_bytes = message.encode('utf-8')

    signature = private_key.sign(
        message_bytes,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )
    return signature

def encrypt_with_public_key(data: bytes, public_key) -> bytes:
    """
    Encrypt the signature using RSA-OAEP with SHA-256.
    """
    ciphertext = public_key.encrypt(
        data,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

def main():
    print("--- GENERATING COMMIT PROOF ---")
    
    # 1. Get Commit Hash
    commit_hash = get_git_commit_hash()
    print(f"✅ Git Commit Hash: {commit_hash}")

    # 2. Load Keys
    student_key, instructor_key = load_keys()

    # 3. Sign the Hash (Proof of Origin)
    signature = sign_message(commit_hash, student_key)
    print("✅ Signed commit hash (RSA-PSS)")

    # 4. Encrypt the Signature (Confidentiality)
    encrypted_signature = encrypt_with_public_key(signature, instructor_key)
    print("✅ Encrypted signature (RSA-OAEP)")

    # 5. Base64 Encode (For Submission)
    final_proof = base64.b64encode(encrypted_signature).decode('utf-8')
    
    print("\n" + "="*60)
    print(f"\nCommit Hash:\n{commit_hash}")
    print(f"\nEncrypted Signature (Single Line):\n{final_proof}")
    print("\n" + "="*60)

if __name__ == "__main__":
    main()