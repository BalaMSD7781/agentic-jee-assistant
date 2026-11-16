import socket
import unittest
from start_local import find_free_port

class LocalLauncherTests(unittest.TestCase):
    def test_busy_port_is_skipped(self):
        with socket.socket() as occupied:
            occupied.bind(('127.0.0.1', 0))
            occupied.listen()
            port = occupied.getsockname()[1]
            if port > 65500:
                self.skipTest('Assigned port is too close to upper bound')
            selected = find_free_port(port, 20)
            self.assertGreater(selected, port)
            with socket.socket() as check:
                check.bind(('127.0.0.1', selected))

    def test_no_free_port_has_clear_message(self):
        with socket.socket() as occupied:
            occupied.bind(('127.0.0.1', 0))
            occupied.listen()
            with self.assertRaises(RuntimeError):
                find_free_port(occupied.getsockname()[1], 1)
