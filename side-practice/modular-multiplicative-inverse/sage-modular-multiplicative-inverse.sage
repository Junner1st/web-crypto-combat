a = 114
b = 58595


'''
install sage:
$ curl -L -O "https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-$(uname)-$(uname -m).sh"
$ bash Miniforge3-$(uname)-$(uname -m).sh
$ conda create -n sage sage python=3.11

use sage:
$ conda activate sage
$ sage sage-modular-multiplicative-inverse.sage
'''

## method 4: sage.all.inverse_mod

a = Integer(a)
b = Integer(b)
print("sage.all.inverse_mod: ", inverse_mod(a, b))