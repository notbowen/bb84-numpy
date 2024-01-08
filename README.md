# BB84 QKD Implementation

## About this Project

This project implements the BB84 QKD protocol using Python and Numpy.
It currently has a basic BB84 implementation allowing users to create and send bits to each other.
The shared bits can then be used for encrypting and decrypting messages.

## Stuff To Do

- [x] Implement a basic quantum API
- [x] Implement a basic BB84 flow
- [x] Implement a eavesdropper and see their effects
- [x] Create a socket-like protocol for communication across programs

## Simple Quantum Protocol (SQP)

> Note from future self: This protocol's design tried to
> copy a HTTP-style protocol. However, this project relies on
> a client-to-client model, unlike HTTP's server-to-client.
> Any request that this protocol sends does not have a clear-cut way
> to determine a response packet, and race conditions may occur.
> Adding a main port to listen for incoming requests, and having multiple
> source ports may fix this issue, but time is of essence and I'm too
> lazy to implement this 😅

A goofy ahh protocol I created for this project. It probably has a lot of
loopholes, bugs and critical security issues, but I am too lazy to figure it out.
Please do not use this for any production apps thanks 🙏

### Message Layout

The SQP message should contain the following fields:

- `Method`: The method type, i.e.: `GET`, `RES`, `ERR`
- `Target`: The hostname of the receiver
- `Sender`: The hostname of the sender
- `Data`: Data to be transferred, can be left as an empty string

### Method Types

There are a variety of method types that are used to send different kinds of data.
All the methods are listed below.

- `MSG`: A message containing encrypted text in the data segment.
- `RES {method}`: A response method to return data to the requester.
- `ERR {method}`: A error method indicating that an error due to the specified method has occurred.
- `GET`: Asks the target to generate a bunch of qubits to derive the key from.
- `BASIS`: Compares the basis of each client. The receiver should send a RES back to the sender.
- `CHECK`: Picks select bits to check for eavesdroppers/errors.

## References

- [https://github.com/MNQuantum/QuantumSimulator/blob/master/python/quantum_simulator.py](https://github.com/MNQuantum/QuantumSimulator/blob/master/python/quantum_simulator.py)
- [https://github.com/Kairos-T/BB84-Simulator](https://github.com/Kairos-T/BB84-Simulator)
- [https://github.com/MNQuantum/QuantumSimulator/](https://www.youtube.com/watch?v=dQw4w9WgXcQ)
