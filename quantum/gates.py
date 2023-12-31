import numpy as np


def get_transposition(n, indices):
    transpose = [0] * n
    k = len(indices)
    ptr = 0
    for i in range(n):
        if i in indices:
            transpose[i] = n - k + indices.index(i)
        else:
            transpose[i] = ptr
            ptr += 1
    return transpose


def apply_gate(gate, *indices):
    axes = (indices, range(len(indices)))

    def op(register):
        return np.tensordot(register, gate, axes=axes).transpose(
            get_transposition(register.ndim, indices)
        )

    return op


def X(index):
    """Generates a Pauli X gate (also called a NOT gate) acting on a given index.
    It returns a function that can be applied to a register."""
    gate = np.array([[0, 1], [1, 0]], dtype=np.complex128)
    return apply_gate(gate, index)


def Z(index):
    """Generates a Pauli Z gate acting on a given index.
    This is the same as a rotation of the Bloch sphere by pi radians about the Z-axis.
    It returns a function that can be applied to a register."""
    gate = np.array([[1, 0], [0, -1]], dtype=np.complex128)
    return apply_gate(gate, index)


def CNOT(i, j):
    """Generates a controlled NOT gate, also called a controlled X gate."""
    gate = np.array([1, 0, 0, 0,
                     0, 1, 0, 0,
                     0, 0, 0, 1,
                     0, 0, 1, 0]
                    ).reshape((2, 2, 2, 2))
    return apply_gate(gate, i, j)


def H(index):
    """Generates a Hadamard gate. It returns a function that can be applied to a register."""
    gate = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
    return apply_gate(gate, index)
