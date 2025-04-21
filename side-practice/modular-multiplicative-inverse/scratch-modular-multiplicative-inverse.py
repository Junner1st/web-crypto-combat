def extended_euclidean(a, b):
    if a == 0:
        return b, 0, 1
    else:
        gcd, x1, y1 = extended_euclidean(b % a, a)
        x = y1 - (b // a) * x1
        y = x1
        return gcd, x, y

def modinv(a, m):
    gcd, x, _ = extended_euclidean(a, m)
    if gcd != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m
    
if __name__ == "__main__":
    a = 114
    b = 58595

    print("modular multiplicative inverse:", modinv(a, b))