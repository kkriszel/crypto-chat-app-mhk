import unittest
import socket
import json

class TestKeyServer(unittest.TestCase):
    KEYSERVER_ADDRESS = ('key-server', 9000)

    def test_register_valid(self):
        request = {'type': 'register', 'client_id': 1, 'public_key': [1, 2, 3]}

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as so:
            so.connect(self.KEYSERVER_ADDRESS)
            so.sendall(json.dumps(request).encode())
            data = so.recv(1024)
            response = json.loads(data.decode())

        self.assertIsNotNone(response)
        self.assertIsNotNone(response.get('status'))
        self.assertEqual(response.get('status'), 'success')

    def test_register_invalid_request_type(self):
        request = {'type': 'this_type_doesnt_exist', 'client_id': 2, 'public_key': [1, 2, 3]}

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as so:
            so.connect(self.KEYSERVER_ADDRESS)
            so.sendall(json.dumps(request).encode())
            data = so.recv(1024)
            response = json.loads(data.decode())

        self.assertIsNotNone(response)
        self.assertIsNotNone(response.get('status'))
        self.assertEqual(response.get('status'), 'error')

    def test_register_invalid_public_key(self):
        request = {'type': 'register', 'client_id': 3, 'public_key': 'not_really_a_public_key'}

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as so:
            so.connect(self.KEYSERVER_ADDRESS)
            so.sendall(json.dumps(request).encode())
            data = so.recv(1024)
            response = json.loads(data.decode())

        self.assertIsNotNone(response)
        self.assertIsNotNone(response.get('status'))
        self.assertEqual(response.get('status'), 'error')

    def test_register_retrieve_valid(self):
        public_key_to_register = [1, 2, 3]

        register_request = {'type': 'register', 'client_id': 42, 'public_key': public_key_to_register}

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as so:
            so.connect(self.KEYSERVER_ADDRESS)
            so.sendall(json.dumps(register_request).encode())
            data = so.recv(1024)
            response = json.loads(data.decode())

        retrieve_request = {'type': 'retrieve', 'client_id': 42}

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as so:
            so.connect(self.KEYSERVER_ADDRESS)
            so.sendall(json.dumps(retrieve_request).encode())
            data = so.recv(1024)
            response = json.loads(data.decode())

        self.assertIsNotNone(response)
        self.assertIsNotNone(response.get('status'))
        self.assertEqual(public_key_to_register, response.get('public_key'))

    def test_register_retrieve_invalid(self):
        retrieve_request = {'type': 'retrieve', 'client_id': 9999999}

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as so:
            so.connect(self.KEYSERVER_ADDRESS)
            so.sendall(json.dumps(retrieve_request).encode())
            data = so.recv(1024)
            response = json.loads(data.decode())

        self.assertIsNotNone(response)
        self.assertIsNotNone(response.get('status'))
        self.assertEqual(response.get('status'), 'error')

if __name__ == '__main__':
    unittest.main()
