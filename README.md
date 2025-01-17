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
