from Crypto.Util.number import inverse
from gmpy2 import invert

a = 114
b = 58595

## method 1: pow
print("built-in inverse: ", pow(a, -1, b))

## method 2: Crypto.Util.number.inverse
print("Crypto.Util.number.inverse: ", inverse(a, b))

## method 3: gmpy2.invert
print("gmpy2.invert: ", invert(a, b))