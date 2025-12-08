# RSA Decryption Logic

import base64
import re
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

def load_private_key(filepath: str = "student_private.pem"):
    """
    Helper function to load your Private Key from the file.
    """
    with open(filepath, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None
        )
    return private_key

def decrypt_seed(encrypted_seed_b64: str, private_key) -> str:
    """
    Decrypts the base64 encoded seed using RSA-OAEP with SHA-256.
    
    Args:
        encrypted_seed_b64: The string you got from the API.
        private_key: Your loaded private key object.
        
    Returns:
        The decrypted 64-character HEX string.
    """
    try:
        # 1. Decode Base64
        ciphertext = base64.b64decode(encrypted_seed_b64)

        # 2. RSA Decryption
        decrypted_bytes = private_key.decrypt(
            ciphertext,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # 3. Convert bytes to string
        decrypted_seed = decrypted_bytes.decode('utf-8')

        # 4. Validation (Crucial!)
        # The instruction says the result MUST be a 64-char hex string.
        if len(decrypted_seed) != 64:
            raise ValueError(f"Invalid seed length: {len(decrypted_seed)}")
        
        # Check if it contains only Hex characters (0-9, a-f)
        if not re.fullmatch(r'^[0-9a-fA-F]{64}$', decrypted_seed):
             raise ValueError("Decrypted seed contains non-hex characters")

        return decrypted_seed

    except Exception as e:
        # If the key is wrong or the text is corrupted, this fails.
        print(f"Decryption Error: {str(e)}")
        raise e