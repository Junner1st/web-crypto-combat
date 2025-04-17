'''
有物不知其數，三三數之剩二，五五數之剩三，七七數之剩二。問物幾何？

表示軍隊人數 x ：
x mod 3 = 2
x mod 5 = 3
x mod 7 = 2
'''

from sage.all import CRT

remainders = [2, 3, 2]
mods = [3, 5, 7]

base_solution = CRT(remainders, mods)
print("the smallest positive solution: ", base_solution)