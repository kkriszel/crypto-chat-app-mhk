# Chat Application implementing the Merkle-Hellman Knapsack Cryptosystem (with Solitaire Stream Cypher)

- **Note**: the listed commands work on UNIX systems. For Windows, check the equivalents (`python3`, `source`, etc.).

## Prerequisites

- **Note**: the application was written in and tested with `python v3.12`.

- Create a virtual environment:

```shell
> python3 -m venv venv
```

- Source the virtual environment:

```shell
> source venv/bin/activate
```

- Install the dependencies:

```shell
> python3 -m pip install -r requirements.txt
```

## Running the keyserver

```shell
> python3 keyserver.py
```

- The keyserver listens on <localhost:9000>.

## Running the client(s)

- To start a client in listening mode:

```shell
> python3 client.py <port>
```

- To start a client which connects to a peer on startup:

```shell
> python3 client.py <port> <peer_port>
```

## Testing

- There are three test suites with unit tests:
  - `test_cyphers.py`
  - `test_mhknapsack.py`
  - `test_keyserver.py`

- To run a test suite:

```shell
> python3 <test_file>
```

- The `test_keyserver.py` suite assumes a running keyserver.

## Sequence diagram of the clients

![sequence_diagram](sequence_diagram.png)

- **Note**: the method names may differ.

## Comprehensive documentation of the project

### Overview

This project is a chat application that implements the Merkle-Hellman Knapsack Cryptosystem and the Solitaire Stream Cypher for secure communication between clients. The application consists of several components, including a key server, clients, and utility functions for cryptographic operations.

### Components

#### Key Server

The key server is responsible for managing and distributing public keys for clients. It listens on a specified port and handles requests to register and retrieve public keys.

#### Client

The client is responsible for generating key pairs, registering public keys with the key server, establishing connections with peers, and encrypting/decrypting messages using the Merkle-Hellman Knapsack Cryptosystem and the Solitaire Stream Cypher. Note that the port that the client listens on is also its ID.

#### Utilities

The utilities module provides various helper functions and classes for cryptographic operations, including modular inverse calculation, binary conversion, and checking if a sequence is superincreasing.

### Cryptographic Systems

#### Merkle-Hellman Knapsack Cryptosystem

The Merkle-Hellman Knapsack Cryptosystem is a public-key cryptosystem based on the subset sum problem. It involves the following steps:

1. **Key Generation**:
    - Generate a superincreasing sequence `w` of length `n`.
    - Choose an integer `q` greater than the sum of all elements in `w`.
    - Find an integer `r` that is coprime to `q`.
    - The private key is `(w, q, r)`.
    - The public key is `beta = (r * w_i) % q` for each `w_i` in `w`.

2. **Encryption**:
    - Convert the message into bits.
    - For each byte, compute the cyphertext `c = sum(a_i * b_i)` where `a_i` are the bits of the byte and `b_i` are the elements of the public key.
    - Return the list of cyphertexts.

3. **Decryption**:
    - Compute the modular inverse `s` of `r` mod `q`.
    - For each cyphertext `c`, compute `c' = c * s % q`.
    - Solve the superincreasing subset sum problem using `c'` and `w` to recover the original byte.

#### Solitaire Stream Cypher

The Solitaire Stream Cypher is a symmetric key stream cypher that uses a deck of cards to generate a pseudo-random keystream. It involves the following steps:

1. **Initialization**:
    - Initialize the deck of cards.

2. **Keystream Generation**:
    - Perform a series of shuffling operations on the deck, including swapping jokers, triple cut, and count cut.
    - Extract the top card value to generate the next byte of the keystream.

3. **Encryption/Decryption**:
    - XOR the keystream bytes with the message bytes to encrypt or decrypt the message.

### Communication

#### Key Server Communication

1. **Register Public Key**:
    - The client sends a request to the key server to register its public key.
    - The key server stores the public key and responds with a success message.

2. **Retrieve Public Key**:
    - The client sends a request to the key server to retrieve the public key of a peer.
    - The key server responds with the public key of the requested peer.

#### Client Communication

1. **Peer Connection**:
    - The client either listens for incoming connections or connects to a peer.
    - The clients exchange initial handshake messages to establish a connection.

2. **Half Key Exchange**:
    - The clients generate and exchange half keys.
    - The half keys are combined to generate a common key, which is used to initialize the Solitaire Stream Cypher.

3. **Message Exchange**:
    - The clients enter a message loop where they alternately send and receive encrypted messages.
    - Messages are encrypted using the Solitaire Stream Cypher and decrypted by the receiving client.
