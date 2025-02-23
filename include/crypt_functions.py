import os
import base64
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.number import long_to_bytes, bytes_to_long, inverse

class AESCipher:
    from Crypto.Cipher import AES
    
    def __init__(self, key = None):
        self.AES_KEY = self.aes_key_generator() if key is None else key

    def aes_key_generator(self, int: length=16):
        # return os.urandom(16)
        '''
        function generateRandomString(length) {
            const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
            // const characters = 'ABCDEFabcdef0123456789';
            let result = '';
            const charactersLength = characters.length;
            for (let i = 0; i < length; i++) {
                result += characters.charAt(Math.floor(Math.random() * charactersLength));
            }
            return result;
        }
        '''


    def encrypt_aes(self, plaintext: str):
        """ 使用 AES-256-CBC 加密 """
        iv = os.urandom(16)  # 產生 16 bytes IV
        cipher = self.AES.new(self.AES_KEY, self.AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(pad(plaintext.encode(), self.AES.block_size))
        
        # 轉成 Base64 方便傳輸
        encrypted_b64 = base64.b64encode(iv + encrypted).decode()
        return encrypted_b64

    def decrypt_aes(self, encrypted_b64: str):
        """ 使用 AES-256-CBC 解密 """
        data = base64.b64decode(encrypted_b64)
        iv = data[:16]  # 取得前 16 bytes 作為 IV
        encrypted = data[16:]
        
        cipher = self.AES.new(self.AES_KEY, self.AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(encrypted), self.AES.block_size)
        
        return decrypted.decode()

class RSACipher:
    """
    public: (n, e)
    private: (n, d)

    encryption: c = m^e mod n
    decryption: m = c^d mod n

    other properties:
            ed ≡ 1      (mod φ(n))
        iff d = e^{-1}  (mod φ(n))
    """
    from Crypto.PublicKey import RSA

    def __init__(self):
        self.public_key, self.private_key = self.rsa_key_generator()

    def rsa_key_generator(self):
        """ 生成 RSA 金鑰 """
        key = self.RSA.generate(2048)
        return (key.n, key.e), (key.n, key.d)
    
    def encrypt_rsa(self, plaintext: str):
        m = bytes_to_long(plaintext.encode())
        n, e = self.public_key
        c = pow(m, n, e)
        return c
    
    def decrypt_rsa(self, c: int):
        n, d = self.private_key
        m = pow(c, n, d)
        return long_to_bytes(m).decode()

        
