import numpy as np

from quantum.base import quantum_register, measure, measure_all
from quantum.gates import H


class QKD:
    def __init__(self, length: int = 16, basis: list[int] | None = None, bits: list[int] | None = None) -> None:
        self.basis = self.random_bits(length) if basis is None else basis
        self.bits = self.random_bits(length) if bits is None else bits
        assert len(self.basis) == len(self.bits) == length

    def random_bits(self, num: int) -> list[int]:
        reg = quantum_register(num)
        for i in range(num):
            reg = H(i)(reg)
        return list(measure_all()(reg))

    def send(self) -> list[np.ndarray]:
        # 1 is hadamard, 0 is computational
        data = []

        for base, bit in zip(self.basis, self.bits):
            reg = quantum_register(1, value=bit)
            if base:
                reg = H(0)(reg)
            data.append(reg)

        return data

    def recv(self, data: list[np.ndarray]) -> None:
        bits = []

        # Align basis
        for base, bit in zip(self.basis, data):
            if base:
                bit = H(0)(bit)
            bits.append(bit)

        # Measure and save all bits
        self.bits = [measure(0)(bit) for bit in bits]

    def prune(self, other_basis: np.ndarray) -> None:
        """Prunes one's bits and basis based on another user's basis.
        Overwrites self.bits with the valid bits. self.basis is not changed
        as it is still needed for the next pruning operation

        Args:
            other_basis (np.ndarray): The basis of the other user
        """

        self.bits = [bit for base, other, bit in zip(self.basis, other_basis, self.bits) if base == other]

    def check_bits(self, other_bits: list[int], threshold: float = 1.0) -> bool:
        """Checks if a certain percentage (100% default) of bits
        match between the sender and receiver.

        Args:
            other_bits (list[int]): The other party's bits
            threshold  (float): The threshold before this function returns false

        Returns:
            bool: Whether a specified percentage of bits match
        """
        
        bit_check = [True if alice == bob else False for alice, bob in zip(self.bits, other_bits)]
        return bit_check.count(True) / len(bit_check) >= threshold
