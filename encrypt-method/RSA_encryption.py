from Crypto.Util.number import getPrime, inverse, bytes_to_long, long_to_bytes
class RSAEncryption(BaseEncryption):
    def __init__(self):
        super().__init__()
        self.n = 0
        self.e = 65537

    def generate_keys(self) -> None:
        
        p = getPrime(512)
        q = getPrime(512)
        self.private_key = long_to_bytes(inverse(self.e, (p-1)*(q-1)))
        self.n = p * q

        n = long_to_bytes(self.n)

        def pad_e(n_len: int, e: bytes) -> bytes:
            return e.to_bytes(n_len, byteorder="big")
        e = pad_e(len(n), self.e)

        self.public_key = n + e
        return

    def exchange_keys(self, peer_data: bytes) -> None:
        self.peer_key = peer_data

    def encrypt(self, plaintext: bytes) -> bytes:
        peer_key_length = len(self.peer_key)
        assert peer_key_length % 2 == 0, "peer_key length must be even"

        n, e = self.peer_key[:peer_key_length//2], self.peer_key[peer_key_length//2:]
        e = bytes_to_long(e.lstrip(b'\x00'))
        n = bytes_to_long(n)
        plaintext_int = bytes_to_long(plaintext)
        if plaintext_int > n:
            raise ValueError("Plaintext too long")
        ciphertext_int = pow(plaintext_int, e, n)
        return long_to_bytes(ciphertext_int)
    
    def decrypt(self, ciphertext: bytes) -> bytes:
        ciphertext_int = bytes_to_long(ciphertext)
        d = int.from_bytes(self.private_key, byteorder="big")
        plaintext_int = pow(ciphertext_int, d, self.n)
        if plaintext_int > self.n:
            raise ValueError("Ciphertext too long")
        return long_to_bytes(plaintext_int)




encrypt_algo = RSAEncryption