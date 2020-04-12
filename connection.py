"""
This module allows to send python strings over the network.
"""
import socket

class connection:
    """
    Class connection allows to send python strings over the network.
    """
    def __init__(self, connection_socket):
        self.connection_socket = connection_socket
        self.status = True

    def close(self):
        """
        Close connection.
        """
        self.connection_socket.shutdown(socket.SHUT_RDWR)
        self.connection_socket.close()

    def get(self):
        """
        Get string.
        """
        buff = bytes()
        elem = bytes(self.connection_socket.recv(1))
        while elem != bytes((0,)) and elem != bytes():
            buff = buff + elem
            elem = bytes(self.connection_socket.recv(1))
        if elem == bytes():
            self.status = False
        return buff.decode()

    def send(self, data: str):
        """
        Send string
        """
        data = bytes(data.encode()) + bytes((0,))
        not_sent = len(data)
        not_sent_data = data
        while not_sent > 0:
            try:
                not_sent -= self.connection_socket.send(not_sent_data)
            except:
                not_sent = 0
                self.status = False
            not_sent_data = data[len(data) - not_sent:]
