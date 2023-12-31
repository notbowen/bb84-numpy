import numpy as np


def quantum_register(num):
    shape = (2,) * num
    first = (0,) * num
    reg = np.zeros(shape, dtype=np.complex128)
    reg[first] = 1+0j
    return reg


def random_register(num):
    shape = (2,) * num
    reg = np.random.randn(*shape) + np.random.randn(*shape) * 1j
    reg = reg / np.linalg.norm(reg)
    return reg


def measure(index):
    def m(register):
        n = register.ndim
        axis = tuple(range(index)) + tuple(range(index + 1, n))
        probs = np.sum(np.abs(register) ** 2, axis=axis)
        p = probs[0] / np.sum(probs)
        s = [slice(0, 2)] * n
        result = int(np.random.rand() > p)
        s[index] = slice(0, 1) if result else slice(1, 2)
        register[tuple(s)] = 0
        register *= 1 / np.linalg.norm(register)
        return result
    return m


def measure_all(collapse=True):
    def m(register):
        r = register.ravel()
        r = r / np.linalg.norm(r)
        index = np.random.choice(range(len(r)), p=np.abs(r)**2)
        multiindex = np.unravel_index(index, register.shape)
        if collapse:
            register.fill(0)
            register[multiindex] = 1.0
        return multiindex
    return m
