from quantum.qkd import QKD
import argparse

def main(bits: int, toggle_eve: bool):
    alice = QKD(bits)
    bob = QKD(bits)

    if toggle_eve:
        eve = QKD(bits)
        eve.recv(alice.send())
        bob.recv(eve.send())
    else:
        bob.recv(alice.send())

    print("Alice's basis:    ", "".join(map(str, alice.basis)))
    print("Bob's basis:      ", "".join(map(str, bob.basis)))

    print("Match?            ", "".join(["x" if alice == bob else " " for alice, bob in zip(alice.basis, bob.basis)]))

    print("Alice's sent bits:", "".join(map(str, alice.bits)))
    print("Bob received bits:", "".join(map(str, bob.bits)))

    print()

    alice.prune(bob.basis)
    bob.prune(alice.basis)

    print("Alice pruned bits:", "".join(map(str, alice.bits)))
    print("Match?            ", "".join(["x" if alice == bob else " " for alice, bob in zip(alice.bits, bob.bits)]))
    print("Bob's pruned bits:", "".join(map(str, bob.bits)))

    if not alice.check_bits(bob.bits):
        print("Eavesdropper detected!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                        prog="A BB84 Simulator",
                        description="A simulator of the BB84 QKD protocol written using Python and Numpy."
        )
    parser.add_argument("-b", "--bits", type=int, help="The number of bits to use", default=16)
    parser.add_argument("-e", "--toggle-eve", action="store_true", help="Drop a eavesdropper between Alice & Bob")

    args = parser.parse_args()
    main(args.bits, args.toggle_eve)
