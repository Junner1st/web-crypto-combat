from Crypto.Util.number import getPrime, inverse, bytes_to_long, long_to_bytes

def gen_key(bits=2048) -> tuple[tuple[int, int], tuple[int, int]]:
    p, q = getPrime(bits // 2), getPrime(bits // 2)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    d = inverse(e, phi)
    return (e, n), (d, n)

def encrypt(plaintext: str, public_key: tuple[tuple[int, int], tuple[int, int]]) -> int:
    e, n = public_key

    plaintext = bytes_to_long(plaintext.encode('utf-8'))
    if plaintext >= n:
        raise ValueError("plaintext too long")
    return pow(plaintext, e, n)

def decrypt(ciphertext, private_key) -> int:
    d, n = private_key
    plaintext = pow(ciphertext, d, n)
    return plaintext

if __name__ == "__main__":
    plaintext = "Take it on a plane, know I smoke the same when I'm on a trip"
    
    public_key, private_key = gen_key()
    ciphertext = encrypt(plaintext, public_key)
    decrypted_int = decrypt(ciphertext, private_key)
    
    print(f"Original: {plaintext}")
    print(f"Encrypted: {ciphertext}")
    print(f"Decrypted: {long_to_bytes(decrypted_int).decode('utf-8')}")



