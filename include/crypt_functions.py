import os
import base64
from Crypto.Util.Padding import pad, unpad
from Crypto.Util.number import long_to_bytes, bytes_to_long, inverse

from Crypto.Cipher import PKCS1_OAEP, AES
from Crypto.PublicKey import RSA
from typing import Literal

class AESCipher:
    
    def __init__(self, key: bytes = None, iv: bytes = None):

        self.AES_KEY: bytes | None = key
        self.AES_IV: bytes | None = iv
        self.cipher: AES.new = None
        # self.cipher = AES.new(self.AES_KEY, self.AES.MODE_CBC, self.AES_IV)
        self.padding_mode: Literal["PKCS7", "zero"] = "PKCS7"
        self.aes_mode: Literal["ECB", "CBC", "CFB", "OFB", "CTR", "OPENPGP", "CCM", "EAX", "SIV", "GCM", "OCB"] = "CBC"
        ''' text from Crypto.Cipher.AES :
            
            MODE_ECB = 1        #: Electronic Code Book (:ref:`ecb_mode`)
            MODE_CBC = 2        #: Cipher-Block Chaining (:ref:`cbc_mode`)
            MODE_CFB = 3        #: Cipher Feedback (:ref:`cfb_mode`)
            MODE_OFB = 5        #: Output Feedback (:ref:`ofb_mode`)
            MODE_CTR = 6        #: Counter mode (:ref:`ctr_mode`)
            MODE_OPENPGP = 7    #: OpenPGP mode (:ref:`openpgp_mode`)
            MODE_CCM = 8        #: Counter with CBC-MAC (:ref:`ccm_mode`)
            MODE_EAX = 9        #: :ref:`eax_mode`
            MODE_SIV = 10       #: Synthetic Initialization Vector (:ref:`siv_mode`)
            MODE_GCM = 11       #: Galois Counter Mode (:ref:`gcm_mode`)
            MODE_OCB = 12       #: Offset Code Book (:ref:`ocb_mode`)
        '''


    def aes_private_key_generator(self, length: int=16):
        # return os.urandom(16)
        '''
        project to client side:

        function generateRandomString(length) {
            const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
            let result = '';
            const charactersLength = characters.length;
            for (let i = 0; i < length; i++) {
                result += characters.charAt(Math.floor(Math.random() * charactersLength));
            }
            return result;
        }
        '''
        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        gen = lambda key_length: ''.join([characters[ord(os.urandom(1)) % len(characters)] for _ in range(key_length)]).encode()
        # gen = lambda len: ''.join([characters[ord(os.urandom(1)) % len(characters)] for _ in range(len)]).encode()
        key = gen(length)
        print(key)
        return key
    
    def set_cipher(self, key: bytes, iv: bytes):
        self.AES_KEY = key
        self.AES_IV = iv
        mode = getattr(AES, f"MODE_{self.aes_mode}")
        # print(f"mode: {mode}")
        self.cipher = AES.new(self.AES_KEY, mode, self.AES_IV)

    # def encrypt_aes(self, plaintext: str):

    #     encrypted = self.cipher.encrypt(pad(plaintext.encode(), AES.block_size))
        
    #     # 轉成 Base64 方便傳輸
    #     encrypted_b64 = base64.b64encode(self.AES_IV + encrypted).decode()
    #     return encrypted_b64

    def decrypt_aes(self, encrypted_b64: bytes):

        self.set_cipher(self.AES_KEY, self.AES_IV)
        base64Decoded = base64.b64decode(encrypted_b64)
        print(f"[AESCipher.decrypt_aes] base64Decoded: {base64Decoded}")
        
        ## is this work ths same?
        # decrypted = self.cipher.decrypt(base64Decoded)
        # decrypted = unpad(decrypted, AES.block_size)
        
        decrypted = self.cipher.decrypt(base64Decoded)
        # print(f"decrypted1: {decrypted}")
        pad_len = decrypted[-1]
        decrypted = decrypted[:-pad_len]
        # print(f"len: {pad_len} | {decrypted}")

        return decrypted.decode()

class RSACipher:
    """
    public: (n, e)
    private: (n, d)

    encryption: c = m^e mod n
    decryption: m = c^d mod n

    other properties:
            ed ≡ 1      (mod φ(n))
        iff d ≡ e^{-1}  (mod φ(n))
    """

    def __init__(self):
        self.public_key, self.private_key = self.rsa_key_generator()
        self.cipher = PKCS1_OAEP.new(self.private_key)

    def rsa_key_generator(self):
        key = RSA.generate(2048)
        public = key.publickey()
        private = key
        return public, private
    
    # def encrypt_rsa(self, plaintext: str):
    #     m = bytes_to_long(plaintext.encode())
    #     n, e = self.public_key
    #     c = pow(m, n, e)
    #     return c
    
    # def decrypt_rsa(self, c: int):
    #     n, d = self.private_key
    #     m = pow(c, n, d)
    #     return long_to_bytes(m).decode()

        
