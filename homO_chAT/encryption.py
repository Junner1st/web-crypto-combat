import abc
from random import randint

class BaseEncryption(abc.ABC):
    """
    加密模組必須實作此介面，
    包含金鑰生成、金鑰交換、加密與解密的基本操作，
    資料以 bytes 進行傳遞
    """
    def __init__(self):
        self.public_key = b""
        self.private_key = b""
        self.peer_key = b""
    
    @abc.abstractmethod
    def generate_keys(self):
        """產生金鑰 (例如公/私鑰或交換用的參數)"""
        pass

    @abc.abstractmethod
    def exchange_keys(self, peer_key: bytes) -> None:
        """接收對方公鑰，更新本地金鑰狀態"""
        pass

    @abc.abstractmethod
    def encrypt(self, plaintext: bytes) -> bytes:
        """對明文進行加密後傳回密文"""
        pass

    @abc.abstractmethod
    def decrypt(self, ciphertext: bytes) -> bytes:
        """對密文進行解密還原成明文"""
        pass

    def get_public_key_info(self) -> str:
        return self.public_key.hex() if self.public_key else ""

    def get_private_key_info(self) -> str:
        return self.private_key.hex() if self.private_key else ""


class DummyEncryption(BaseEncryption):
    """
    測試用的演算法，所有操作均為單位操作，不對明文做任何改變
    """
    def generate_keys(self) -> None:
        return

    def exchange_keys(self, peer_key: bytes) -> None:
        return

    def encrypt(self, plaintext: bytes) -> bytes:
        return plaintext

    def decrypt(self, ciphertext: bytes) -> bytes:
        return ciphertext


class CaesarEncryption(BaseEncryption):
    """
    把英文字母往後「固定向後移動幾格」的加密方法
    如要加密 "Apple"，key 是 1
    加密後變 "Bqqmf"
    解密只要每個字「倒退 key 格」即可
    """
    def generate_keys(self) -> None:
        self.public_key = bytes([randint(0, 25)])
        self.private_key = self.public_key
        return

    def exchange_keys(self, peer_data: bytes) -> None:
        self.peer_key = peer_data

    def encrypt(self, plaintext: bytes) -> bytes:
        key = int.from_bytes(self.peer_key, byteorder="big")
        cipher = bytearray()
        for b in plaintext:
            if 97 <= b <= 122:  # ord('a') = 97; ord('z') = 122
                cipher.append((b - 97 + key) % 26 + 97)
            elif 65 <= b <= 90:  # ord('A') = 65; ord('Z') = 90
                cipher.append((b - 65 + key) % 26 + 65)
            else:
                cipher.append(b)
        return bytes(cipher)
    
    def decrypt(self, ciphertext: bytes) -> bytes:
        key = int.from_bytes(self.private_key, byteorder="big")
        plain = bytearray()
        for b in ciphertext:
            if 97 <= b <= 122:  # ord('a') = 97; ord('z') = 122
                plain.append((b - 97 - key) % 26 + 97)
            elif 65 <= b <= 90:  # ord('A') = 65; ord('Z') = 90
                plain.append((b - 65 - key) % 26 + 65)
            else:
                plain.append(b)
        return bytes(plain)

encrypt_algo = CaesarEncryption

# 使用哪個加密演算法可以在程式碼中輕易替換
# 預設可以用 DummyEncryption 或 CaesarEncryption 進行測試。
if __name__ == '__main__':
    # 簡單測試
    algo = CaesarEncryption()
    algo.generate_keys()
    plaintext = b"Hello, World!"
    algo.exchange_keys(algo.public_key)
    ciphertext = algo.encrypt(plaintext)
    decrypted = algo.decrypt(ciphertext)
    print("Key:", algo.get_public_key_info())
    print("Ciphertext:", ciphertext)
    print("Decrypted:", decrypted)
