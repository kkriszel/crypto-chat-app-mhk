import socket
import json
import structlog
from logging import Logger

import utils

class KeyServer:
    public_keys: dict[int, list[int]]
    logger: Logger

    SERVER_ADDR = ('localhost', 9000)

    def __init__(self) -> None:
        """
        Initialize the KeyServer instance.
        """
        self.public_keys = {}
        self.logger = structlog.get_logger()

    def start(self) -> None:
        """
        Start the key server to listen for incoming client connections and handle their requests.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                try:
                    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    server_socket.bind(self.SERVER_ADDR)
                    server_socket.listen()

                    self.logger.info(f'Key Server is listening on {self.SERVER_ADDR}')

                    while True:
                        try:
                            client_socket, client_address = server_socket.accept()
                            self.logger.info('Accepted client socket from:', client_address=client_address)
                            with client_socket:
                                data = client_socket.recv(1024)

                                try:
                                    request = json.loads(data.decode())
                                    self.logger.info('Request:', request=request)
                                    response = self._handle_request(request)
                                except json.JSONDecodeError as e:
                                    self.logger.error(f'Invalid JSON request, exception: {e}')
                                    response = {'status': 'error', 'message': 'Invalid JSON request'}

                                self.logger.info('Response:', response=response)
                                client_socket.sendall(json.dumps(response).encode())
                        except socket.error as e:
                            self.logger.error(f'Client socket error: {e}')
                except socket.error as e:
                    self.logger.error(f'Server socket error: {e}')
        except KeyboardInterrupt:
            self.logger.info('Server interrupted by user')

    def _handle_request(self, request: dict) -> dict:
        """
        Handle incoming requests from clients.

        Args:
            request (dict): The request received from a client.

        Returns:
            dict: The response to be sent back to the client.
        """
        request_type = request.get('type')

        if request_type == 'register':
            return self._handle_register_request(request)
        elif request_type == 'retrieve':
            return self._handle_retrieve_request(request)
        else:
            self.logger.error('Invalid request type:', request_type=request_type)
            return {'status': 'error', 'message': 'Invalid request type'}

    def _handle_register_request(self, request: dict) -> dict:
        """
        Handle a public key registration request from a client.

        Args:
            request (dict): The registration request containing the client ID and public key.

        Returns:
            dict: The response indicating the success or failure of the registration.
        """
        client_id = request.get('client_id')
        public_key = request.get('public_key')

        if client_id and public_key:
            if not utils.is_list_of_ints(public_key):
                self.logger.error('Invalid register request')
                return {'status': 'error', 'message': 'Specified public key is not a list of ints'}

            self.public_keys[client_id] = public_key
            self.logger.info('Public key registered for:', client_id=client_id)
            return {'status': 'success', 'message': 'Public key registered'}
        else:
            self.logger.error('Invalid register request')
            return {'status': 'error', 'message': 'Invalid register request'}

    def _handle_retrieve_request(self, request: dict) -> dict:
        """
        Handle a public key retrieval request from a client.

        Args:
            request (dict): The retrieval request containing the client ID.

        Returns:
            dict: The response containing the public key or an error message.
        """
        client_id = request.get('client_id')

        if not client_id:
            self.logger.error('Invalid retrieve request, missing client_id')
            return {'status': 'error', 'message': 'client_id is missing or null'}

        if client_id in self.public_keys:
            public_key = self.public_keys[client_id]
            self.logger.info('Public key retrieved for:', client_id=client_id)
            return {'status': 'success', 'public_key': public_key}
        else:
            self.logger.error('Entry not found:', client_id=client_id)
            return {'status': 'error', 'message': 'client_id not found'}

if __name__ == '__main__':
    key_server = KeyServer()
    key_server.start()
