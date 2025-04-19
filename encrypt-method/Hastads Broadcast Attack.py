''' 
RSA design:
n = p * q
e = 65537 s.t. (1 < e < phi(n) and gcd(e, phi(n)) = 1)
public key : (n, e)
private key : d = e^-1 mod phi(n)

chinese remainder theorem:
p = c1 mod m1
p = c2 mod m2
p = c3 mod m3
'''
from Crypto.Util.number import inverse, long_to_bytes, bytes_to_long
from sage.all import CRT
from gmpy2 import iroot
from math import gcd
cipher_list = [
    
]
c1 = int("74c5ced7bf7e878d70c7ee5b0910ed1eb7c91e515f3bdfe01fdfaa0f6547d01188e2cc29f7e3114d61ff75a4b7afbaf9c72a8ac162f95b8c3356726f9a30dcd85f17bcf42c02c9366c43eacb2d975aec6482d932942e260b6b375cb7806b1232eef84d8dd42b59d31733a614ff615fa3406632c5ba10b7bbe07491b781674e1e", 16)
c2 = int("6f4d8f1c227f947ae27dc24b696d83549253cdf97a553c38641ab5dc71725739cee3e3a2d8141bd80229dc7806a9fefc8c1fa1169af79d38539d0a8af8397b446097e1c1849ab6d54444c745953caeef704bc8fb19034eecca79315f06378c14d3e5b39f4cc0998a1ab5c4d5e0fcae2174becd8ac6e7cf99d2544b3548c1a1b5", 16)

e = 65537

def parse_key(key: bytes) -> tuple:
    key_length = len(key)
    assert key_length % 2 == 0, "key length must be even"
    n, e = key[:key_length//2], key[key_length//2:]
    e = bytes_to_long(e.rstrip(b'\x00'))
    n = bytes_to_long(n)
    return n, e

peer_key1 = bytes.fromhex("bf3ee9f0e4991ce3c5a9441d6f59054695e1014a392c08da7d6b1a146c0f970b09ca73c01dceea1b3681813f5fb2790fde3ccf8fe703977852df043d5cb8fdf853486176ff22f2c8cb30049e047b5fa3ec92c1c2815e5ce5814abcf7a433af664654d4d9ea0fd300d63c08775f190b0425b10e01c77ea9370fd345457e9b70cd0100010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
n1, _ = parse_key(peer_key1)

peer_key2 = bytes.fromhex("90b457984ec619d9c389b4fdada919207f6c40c08523c4de0825c478863e6e2dce4954640a5c6e34c73d9b3b000a6ed46836ffcb120e8004bbdc81ac75c4cc6571b5d2e842bdafff0447449de87bea13e5e083f0131b32aeb3a23be571181856a8fb4456f6ac091613baf78945e3955ac11caa01c7c67db9b8a18e10a7436d3d0100010000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
n2, _ = parse_key(peer_key2)


if gcd(n1, n2) != 1:
    raise ValueError("n1 and n2 are not coprime")

crt_ans = CRT([c1, n1], [c2, n2])
print(crt_ans)
plaintext = iroot(crt_ans, e)

print(plaintext)