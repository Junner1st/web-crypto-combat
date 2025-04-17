def extended_euclidean(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = extended_euclidean(b % a, a)
        return (g, x - (b // a) * y, y)

def modinv(a, m):
    g, x, y = extended_euclidean(a, m)
    if g != 1:
        raise Exception('modular inverse does not exist')
    else:
        return x % m
    

a = 114
b = 58595

print("scratch modular multiplicative inverse: ", modinv(a, b))