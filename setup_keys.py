# Script to generate RSA key pair and save to PEM files

def generate_rsa_keypair(key_size: int = 4096):
    """
    Generate RSA key pair

    Returns:
        Tuple of (private_key, public_key) objects

    Implementation:
    - Use your language's crypto library to generate 4096-bit RSA key
    - Set public exponent to 65537
    - Serialize to PEM format
    - Return key objects for further use
    """
    from cryptography.hazmat.primitives.asymmetric import rsa
    from cryptography.hazmat.primitives import serialization

    # Generate the Private Key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )

    # Generate the Public Key
    public_key = private_key.public_key()

    return private_key, public_key


def save_key_to_pem(key, filename: str, is_private: bool = True):
    """
    Save RSA key to PEM file

    Args:
        key: RSA key object (private or public)
        filename: Output filename
        is_private: Boolean indicating if the key is private
    """
    from cryptography.hazmat.primitives import serialization

    if is_private:
        pem_data = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
    else:
        pem_data = key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    with open(filename, "wb") as f:
        f.write(pem_data)


if __name__ == "__main__":
    print("Generating 4096-bit RSA Keys... (this might take a moment)")
    private_key, public_key = generate_rsa_keypair()

    save_key_to_pem(private_key, "student_private.pem", is_private=True)
    save_key_to_pem(public_key, "student_public.pem", is_private=False)

    print("✅ Success! 'student_private.pem' and 'student_public.pem' created.")
