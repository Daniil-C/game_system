import socket
import os

if __name__ == "__main__":
    LISTENING_SOCKET = socket.socket()
    IP_ADDRESS = os.getenv["HOST_IP"]
    PORT = os.getenv["PORT"]
    LISTENING_SOCKET.bind((IP_ADDRESS, PORT))
    LISTENING_SOCKET.listen()
