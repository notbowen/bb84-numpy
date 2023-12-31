import numpy as np

from quantum.base import quantum_register, measure_all
from quantum.gates import H

def random_bits(num):
    reg = quantum_register(num)
    for i in range(num):
        reg = H(i)(reg)
    return measure_all()(reg)

for i in range(10):
    print("".join(map(str, random_bits(10))))
