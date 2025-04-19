from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from Crypto.Hash import BLAKE2s

class AES_CBC_Encryption(BaseEncryption):
    def __init__(self):
        super().__init__()
        self._mac_tag = None
        self._mac_tag_size = 20  # bytes ## for blake2s, usually 20 bytes

    def verify(self, received_mac_tag) -> bool:
        secret = get_random_bytes(16)

        mac1 = BLAKE2s.new(digest_bits=(8*self._mac_tag_size), key=secret,
                           data=self._mac_tag)
        mac2 = BLAKE2s.new(digest_bits=(8*self._mac_tag_size), key=secret,
                           data=received_mac_tag)

        if mac1.digest() != mac2.digest():
            print("MAC check failed")
            return False
        else:
            print("MAC check passed")
            return True

    def generate_keys(self) -> None:
        self.public_key = get_random_bytes(32)  # 16 bits key + 16 bits iv
        self.private_key = self.public_key
        return

    def exchange_keys(self, peer_data: bytes) -> None:
        self.peer_key = peer_data

    def encrypt(self, plaintext: bytes) -> bytes:
        key, iv = self.peer_key[:16], self.peer_key[16:]
        mac_tag = BLAKE2s.new(digest_bits=(8*self._mac_tag_size), key=key,
                                   data=plaintext).digest()
        # middle_man_message = b""

        ### 假設被中間人篡改消息
        middle_man_message = "現在正是復權的時刻".encode('utf-8')

        plaintext = plaintext + middle_man_message
        cipher = AES.new(key, AES.MODE_CBC, iv)
        ciphertext = cipher.encrypt(pad(plaintext, 16))

        return ciphertext + mac_tag

    def decrypt(self, ciphertext: bytes) -> bytes:
        ciphertext, received_mac_tag = ciphertext[:-self._mac_tag_size], ciphertext[-self._mac_tag_size:]
        key, iv = self.private_key[:16], self.private_key[16:]

        decipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = unpad(decipher.decrypt(ciphertext), 16)

        self._mac_tag = BLAKE2s.new(digest_bits=(8*self._mac_tag_size), key=key,
                                   data=plaintext).digest()
        VERIFY_SUCCESS = self.verify(received_mac_tag)
        if not VERIFY_SUCCESS:
            plaintext = b" [message TAMPERED]" + plaintext
        else:
            plaintext = b" [message VERIFIED]" + plaintext

        return plaintext
    
