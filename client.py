import socket
import json
import argparse
from mhknapsack import MHKnapsack
import structlog
from logging import Logger
import sys
import random
from cyphers import StreamCypher, SolitaireKeyStream

class Client:
    KEYSERVER_ADDRESS = ('localhost', 9000)

    client_id: int
    private_key: tuple[tuple[int, ...], int, int]
    public_key: tuple[int, ...]
    logger: Logger
    own_socket: socket.socket | None
    peer_socket: socket.socket | None
    peer_id: int | None
    peer_success: bool
    peer_public_key: tuple[int, ...] | None
    should_start: bool | None
    half_key: int | None
    peer_half_key: int | None
    common_key: list[int] | None
    stream_cypher: StreamCypher | None

    def __init__(self, client_id: int, peer_id: int | None=None) -> None:
        """
        Initialize the Client instance.

        Args:
            client_id (int): The ID of the client.
            peer_id (int, optional): The ID of the peer client. Defaults to None.
        """
        self.client_id = client_id
        self.logger = structlog.get_logger()
        self.own_socket = None
        self.peer_socket = None
        self.peer_id = peer_id
        self.peer_success = False
        self.should_start = None
        self.half_key = None
        self.peer_half_key = None
        self.common_key = None
        self.stream_cypher = None

    def start(self) -> None:
        """
        Start the client operations including key generation, registration, peer connection,
        key exchange, and message loop.
        """
        try:
            self._generate_key_pair()
            self._register_public_key()
            self._peer()
            self._generate_half_key()
            self._exchange_half_keys()
            self._generate_common_key()
            self._init_stream_cypher()
            self._message_loop()
        except Exception as e:
            self.logger.error(f'Error in base: {e}')
        finally:
            self._cleanup()

    def _generate_key_pair(self) -> None:
        """
        Generate a private and public key pair using the MHKnapsack algorithm.
        """
        self.private_key = MHKnapsack.generate_private_key()
        self.public_key = MHKnapsack.create_public_key(self.private_key)

    def _register_public_key(self) -> None:
        """
        Register the client's public key with the key server.
        """
        request = {
            'type': 'register',
            'client_id': self.client_id,
            'public_key': list(self.public_key),
        }

        self.logger.info('Public key registering request:', request=request)

        try:
            response = self._communicate_keyserver(request)
        except RuntimeError as e:
            self.logger.error(f'Error sending registering public key: {e}')
            sys.exit(1)

        if response.get('status') != 'success':
            self.logger.error(f'Error: {response.get("message")}')
            sys.exit(1)

        self.logger.info('Public key registering response:', response=response)

    def _peer(self) -> None:
        """
        Attempt to connect to a peer client. If no peer ID is provided, listen for incoming connections.
        """
        if not self.peer_id:
            listen_success = self._try_listen()

            if listen_success:
                return

        self._try_connect()

    def _generate_half_key(self) -> None:
        """
        Generate a random half key for the key exchange process.
        """
        self.half_key = random.randint(10000, 9999999)
        self.logger.info('Generated own half key:', half_key=self.half_key)

    def _exchange_half_keys(self) -> None:
        """
        Exchange half keys with the peer client to generate a common key.
        """
        if self.should_start:
            self._send_own_half_key()
            self._receive_peer_half_key()
        else:
            self._receive_peer_half_key()
            self._send_own_half_key()

    def _generate_common_key(self) -> None:
        """
        Generate a common key using the exchanged half keys.
        """
        common_key = self.half_key * self.peer_half_key
        random.seed(common_key)

        self.common_key = list(range(1, 55))
        random.shuffle(self.common_key)

        self.logger.info('Generated common key:', key=self.common_key)

    def _init_stream_cypher(self) -> None:
        """
        Initialize the stream cypher using the generated common key.
        """
        key_stream = SolitaireKeyStream(self.common_key)
        self.stream_cypher = StreamCypher(key_stream)
        self.logger.info('Stream cypher initialized')

    def _message_loop(self) -> None:
        """
        Start the message loop for sending and receiving messages with the peer client.
        """
        self.logger.info('Starting message loop. To stop, type \'exit\' in your round.')

        try:
            if self.should_start:
                self._send_message()

            while True:
                self._receive_message()
                self._send_message()
        except InterruptedError:
            pass

        self.logger.info('Messaging over. Goodbye!')

    def _send_message(self) -> None:
        """
        Send an encrypted message to the peer client.
        """
        msg_input = input('>  You: ')

        should_finish = msg_input == 'exit'

        msg = {'over': False, 'message': msg_input} if not should_finish else {'over': True}
        msg_data = self._to_encrypted_bytes_sks(msg)
        # self.logger.debug('Encrypted message to be sent:', msg=msg_data)

        try:
            self.peer_socket.sendall(msg_data)
        except socket.error as e:
            self.logger.error(f'Error sending to peer: {e}')
            raise RuntimeError('Error sending to peer')

        if should_finish:
            raise InterruptedError

    def _receive_message(self) -> None:
        """
        Receive and decrypt a message from the peer client.
        """
        print('> Peer: ', end='', flush=True)

        try:
            msg_data = self.peer_socket.recv(4048)
        except socket.error as e:
            self.logger.error(f'Error receiving from peer: {e}')
            raise RuntimeError('Error receiving from peer')

        # self.logger.debug('Encrypted message received:', msg=msg_data)
        msg = self._from_encrypted_bytes_sks(msg_data)

        if msg.get('over') is True:
            print('exit')
            raise InterruptedError

        print(msg.get('message'))

    def _cleanup(self) -> None:
        """
        Clean up resources by closing the sockets.
        """
        if self.own_socket:
            self.own_socket.close()
        if self.peer_socket:
            self.peer_socket.close()

    def _try_listen(self) -> bool:
        """
        Attempt to listen for incoming connections from a peer client.

        Returns:
            bool: True if a peer connection is successfully accepted, False otherwise.
        """
        self.own_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.own_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.own_socket.bind(('localhost', self.client_id))
            self.own_socket.listen()

            self.logger.info('Listening on own socket. Press Ctrl+C to stop listening and connect to a peer instead.')

            while True:
                try:
                    self.peer_socket, peer_address = self.own_socket.accept()
                    self.logger.info('Accepted client socket from:', incoming_address=peer_address)

                    init_data = self.peer_socket.recv(1024)
                    init_msg = self._from_encrypted_bytes_mhk(init_data, self.private_key)

                    self.logger.info('Received init message:', init_msg=init_msg)

                    peer_id = init_msg.get('client_id')

                    if peer_id is None and not isinstance(peer_id, int):
                        self.logger.warn('Invalid peer handshake')
                        continue

                    self.peer_id = peer_id
                    self._retrieve_peer_public_key()

                    ack_msg = {'status':'ok'}
                    ack_data = self._to_encrypted_bytes_mhk(ack_msg, self.peer_public_key)

                    self.logger.info('Sending ack message:', ack_msg=ack_msg)
                    self.peer_socket.sendall(ack_data)

                    self.peer_success = True
                    self.should_start = False
                    return True
                except socket.error as e:
                    self.logger.error(f'Error accepting peer: {e}')
                    sys.exit(1)
                finally:
                    if self.peer_socket and not self.peer_success:
                        self.peer_socket.close()
        except socket.error as e:
            self.logger.error(f'Error listening on own socket: {e}')
            raise RuntimeError('Error listening on own socket')
        except KeyboardInterrupt:
            self.logger.info('Listening interrupted by user')
            return False
        finally:
            if self.own_socket and not self.peer_success:
                self.own_socket.close()

    def _try_connect(self) -> None:
        """
        Attempt to connect to a peer client using the provided peer ID.
        """
        if not self.peer_id:
            peer_id = None
            while not peer_id and peer_id == self.peer_id:
                try:
                    peer_id = int(input('> Enter the port (client_id) of the peer: '))
                except ValueError:
                    pass
            self.peer_id = peer_id

        self._retrieve_peer_public_key()

        self.peer_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.peer_socket.connect(('localhost', self.peer_id))

            self.logger.info('Connected to peer')

            init_msg = {'client_id': self.client_id}

            init_data = self._to_encrypted_bytes_mhk(init_msg, self.peer_public_key)

            self.logger.info('Sending init message:', init_msg=init_msg)
            self.peer_socket.sendall(init_data)

            ack_data = self.peer_socket.recv(1024)
            ack_msg = self._from_encrypted_bytes_mhk(ack_data, self.private_key)

            self.logger.info('Received ack message:', ack_msg=ack_msg)

            if ack_msg.get('status') != 'ok':
                self.logger.error('Peer did not accept the handshake')
                sys.exit(1)

            self.peer_success = True
            self.should_start = True
        except socket.error as e:
            self.logger.error(f'Error connecting to peer: {e}')
            raise ValueError('Error connecting to peer')
        finally:
            if self.peer_socket and not self.peer_success:
                self.peer_socket.close()

    def _retrieve_peer_public_key(self) -> None:
        """
        Retrieve the public key of the peer client from the key server.
        """
        request = {
            'type': 'retrieve',
            'client_id': self.peer_id,
        }

        self.logger.info('Peer public key retrieving request:', request=request)

        try:
            response = self._communicate_keyserver(request)
        except socket.error as e:
            self.logger.error(f'Error retrieving peer public key: {e}')
            raise RuntimeError('Error retrieving peer public key')

        if response.get('status') != 'success':
            self.logger.error(f'Error: {response.get("message")}')
            raise RuntimeError('Error from keyserver')

        self.logger.info('Peer public key retrieving response:', response=response)
        self.peer_public_key = tuple(response.get('public_key'))

    def _communicate_keyserver(self, request: dict) -> dict:
        """
        Communicate with the key server to send a request and receive a response.

        Args:
            request (dict): The request to send to the key server.

        Returns:
            dict: The response from the key server.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as so:
                so.connect(self.KEYSERVER_ADDRESS)
                so.sendall(json.dumps(request).encode())
                data = so.recv(1024)
                return json.loads(data.decode())
        except socket.error as e:
            self.logger.error(f'Error communicating with keyserver socket: {e}')
            raise RuntimeError(e)

    def _send_own_half_key(self) -> None:
        """
        Send the client's half key to the peer client.
        """
        try:
            msg = {'half_key': self.half_key}
            msg_data = self._to_encrypted_bytes_mhk(msg, self.peer_public_key)

            self.logger.info('Sending own half key:', msg=msg)
            self.peer_socket.send(msg_data)
        except socket.error as e:
            self.logger.error(f'Error sending own half key: {e}')
            sys.exit(1)

    def _receive_peer_half_key(self) -> None:
        """
        Receive the peer client's half key.
        """
        try:
            msg_data = self.peer_socket.recv(1024)
            msg = self._from_encrypted_bytes_mhk(msg_data, self.private_key)
            self.logger.info('Received peer half key:', msg=msg)
            self.peer_half_key = msg.get('half_key')
        except socket.error as e:
            self.logger.error(f'Error receiving peer half key: {e}')
            sys.exit(1)

    def _to_encrypted_bytes_mhk(self, msg: dict, public_key: tuple[int, ...]) -> bytes:
        """
        Encrypt a message using the MHKnapsack algorithm and convert it to bytes.

        Args:
            msg (dict): The message to encrypt.
            public_key (tuple[int, ...]): The public key for encryption.

        Returns:
            bytes: The encrypted message in bytes.
        """
        msg_json_str = json.dumps(msg)
        msg_json_bytes = msg_json_str.encode()
        msg_json_encrypted = MHKnapsack.encrypt(msg_json_bytes, public_key)
        msg_json_encrypted_json_str = json.dumps(msg_json_encrypted)
        msg_json_encrypted_json_bytes = msg_json_encrypted_json_str.encode()
        return msg_json_encrypted_json_bytes

    def _from_encrypted_bytes_mhk(self, msg: bytes, private_key: tuple[tuple[int, ...], int, int]) -> dict:
        """
        Decrypt a message using the MHKnapsack algorithm from bytes.

        Args:
            msg (bytes): The encrypted message in bytes.
            private_key (tuple[tuple[int, ...], int, int]): The private key for decryption.

        Returns:
            dict: The decrypted message.
        """
        msg_json_encrypted_json_str = msg.decode()
        msg_json_encrypted = json.loads(msg_json_encrypted_json_str)
        msg_json_bytes = MHKnapsack.decrypt(msg_json_encrypted, private_key)
        msg_json_str = msg_json_bytes.decode()
        msg_json = json.loads(msg_json_str)
        return msg_json

    def _to_encrypted_bytes_sks(self, msg: dict) -> bytes:
        """
        Encrypt a message using the stream cypher and convert it to bytes.

        Args:
            msg (dict): The message to encrypt.

        Returns:
            bytes: The encrypted message in bytes.
        """
        msg_json_str = json.dumps(msg)
        msg_json_bytes = msg_json_str.encode()
        msg_json_encrypted = self.stream_cypher.encode(msg_json_bytes)
        return msg_json_encrypted

    def _from_encrypted_bytes_sks(self, msg: bytes) -> dict:
        """
        Decrypt a message using the stream cypher from bytes.

        Args:
            msg (bytes): The encrypted message in bytes.

        Returns:
            dict: The decrypted message.
        """
        msg_json_bytes = self.stream_cypher.decode(msg)
        msg_json_str = msg_json_bytes.decode()
        msg_json = json.loads(msg_json_str)
        return msg_json

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('port', type=int, help='Port number (also client_id) for the client')
    parser.add_argument('peer_port', type=int, nargs='?', default=None, help='Port number (also client_id) for the peer')
    args = parser.parse_args()

    client_id = args.port
    peer_id = args.peer_port

    key_client = Client(client_id, peer_id)
    key_client.start()
