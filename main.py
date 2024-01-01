from quantum.qkd import QKD

alice = QKD()
bob = QKD()
eve = QKD()

eve.recv(alice.send())
bob.recv(eve.send())
# bob.recv(alice.send())

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
