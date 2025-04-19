from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

class AES_CBC_Encryption(BaseEncryption):

    def generate_keys(self) -> None:
        self.public_key = get_random_bytes(32)  # 16 bits key + 16 bits iv
        self.private_key = self.public_key
        return

    def exchange_keys(self, peer_data: bytes) -> None:
        self.peer_key = peer_data

    def encrypt(self, plaintext: bytes) -> bytes:
        key, iv = self.peer_key[:16], self.peer_key[16:]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(plaintext, 16))

        return ciphertext

    def decrypt(self, ciphertext: bytes) -> bytes:
        key, iv = self.private_key[:16], self.private_key[16:]
        decipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = unpad(decipher.decrypt(ciphertext), 16)

        return plaintext

encrypt_algo = AES_CBC_Encryption