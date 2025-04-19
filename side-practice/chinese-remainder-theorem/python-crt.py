from functools import reduce
def chinese_remainder(moduli, remainders):
    total = 0
    product = reduce(lambda acc, n: acc * n, moduli)

    for modulus, remainder in zip(moduli, remainders):
        partial_product = product // modulus
        inverse = modular_inverse(partial_product, modulus)
        total += remainder * inverse * partial_product

    return total % product

def modular_inverse(a, modulus):
    original_modulus = modulus
    x0, x1 = 0, 1

    if modulus == 1:
        return 1

    while a > 1:
        quotient = a // modulus
        a, modulus = modulus, a % modulus
        x0, x1 = x1 - quotient * x0, x0

    if x1 < 0:
        x1 += original_modulus

    return x1

if __name__ == '__main__':
    moduli = [3, 5, 7]
    remainders = [2, 3, 2]

    result = chinese_remainder(moduli, remainders)
    print(f"Chinese Remainder Theorem: {result}")











    