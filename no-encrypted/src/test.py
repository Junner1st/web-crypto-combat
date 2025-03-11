from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import base64

def aes_encrypt(plain_text, key, iv):
    cipher = AES.new(key, AES.MODE_CBC, iv)  # 創建加密對象
    print(f"pad: {pad(plain_text.encode('utf-8'), AES.block_size)}")
    encrypted = cipher.encrypt(pad(plain_text.encode('utf-8'), AES.block_size))  # 加密並補位
    return base64.b64encode(encrypted).decode('utf-8')  # 返回加密後的資料（含IV）

def aes_decrypt(encrypted_text, key, iv):
    encrypted_bytes = base64.b64decode(encrypted_text)  # 解碼
    # iv = encrypted_bytes[:16]  # 提取IV
    # encrypted_data = encrypted_bytes[16:]  # 提取加密資料
    cipher = AES.new(key, AES.MODE_CBC, iv)  # 創建解密對象
    decrypted = unpad(cipher.decrypt(encrypted_bytes), AES.block_size).decode('utf-8')  # 解密並去補位
    return decrypted

def main():
    # key = get_random_bytes(16)  # 128位元密鑰
    # iv = get_random_bytes(16)  # 生成隨機初始化向量
    # key = bytes.fromhex('31324744533334353637386468737468')
    # iv = bytes.fromhex('65664631324744533334354136373864')
    key = b'12GDS345678dhsth'
    iv = b'efF12GDS345A678d'
    print(key.hex())
    print(iv.hex())

    plain_text = "Happy Birthday!"  # 要加密的明文
    
    print(f"明文: {plain_text}")
    
    encrypted = aes_encrypt(plain_text, key, iv)  # 加密
    print(f"加密後: {encrypted}")
    
    decrypted = aes_decrypt(encrypted, key, iv)  # 解密
    print(f"解密後: {decrypted}")

if __name__ == "__main__":
    main()