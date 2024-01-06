# BB84 QKD Implementation

## About this Project

This project aims to implement the BB84 QKD protocol using Python and Numpy.
Currently has a basic BB84 implementation allowing users to create and send bits to each other.

## Stuff To Do

- [x] Implement a basic quantum API
- [x] Implement a basic BB84 flow
- [x] Implement a eavesdropper and see their effects
- [ ] Create a socket-like protocol for communication across programs

## Simple Quantum Protocol (SQP)

A goofy ahh protocol I created for this project. It probably has a lot of
loopholes, bugs and critical security issues, but I am too lazy to figure it out.
Please do not use this for any production apps thanks 🙏

This documentation is a work in progress.

### Message Layout

The SQP message should contain the following fields:

- Method: The method type, i.e.: `GET`, `RES`, `ERR`
- Target: The hostname of the receiver
- Sender: The hostname of the sender
- Data: Data to be transferred, can be left as an empty string

### Method Types

There are a variety of method types that are used to send different kinds of data.
All the methods are listed below.

- `MSG`: A message containing text in the data segment.
- `RES`: A response method to return data to the requester.
- `ERR`: A error method indicating that an error has occurred.
- `GET`: Asks the target to generate a bunch of qubits to derive the key from.
- `BASIS`: Compares the basis of each client. The receiver should send a RES back to the sender.
- `CHECK`: Picks select bits to check for eavesdroppers/errors.

## References

- [https://github.com/MNQuantum/QuantumSimulator/blob/master/python/quantum_simulator.py](https://github.com/MNQuantum/QuantumSimulator/blob/master/python/quantum_simulator.py)
- [https://github.com/Kairos-T/BB84-Simulator](https://github.com/Kairos-T/BB84-Simulator)
