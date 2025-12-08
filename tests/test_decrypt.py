from app.crypto_utils import decrypt_seed, load_private_key

def test():
    print("Testing Decryption...")
    
    # 1. Load your key
    try:
        pk = load_private_key("student_private.pem")
        print("✅ Private Key loaded.")
    except FileNotFoundError:
        print("❌ Error: student_private.pem not found.")
        return

    # 2. Load the encrypted seed
    try:
        with open("encrypted_seed.txt", "r") as f:
            enc_seed = f.read().strip() # Remove any accidental whitespace
        print("✅ Encrypted Seed loaded.")
    except FileNotFoundError:
        print("❌ Error: encrypted_seed.txt not found. Run get_seed.py first.")
        return

    # 3. Attempt Decryption
    try:
        decrypted = decrypt_seed(enc_seed, pk)
        print("\n🎉 SUCCESS! Decryption worked.")
        print(f"Decrypted Seed: {decrypted}")
        print("(This is your secret 64-char Hex Seed)")
    except Exception as e:
        print(f"\n❌ FAILED: {e}")

if __name__ == "__main__":
    test()