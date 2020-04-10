"""
Server for Imaginarium game
"""
import socket
import os
import server.server_main


if __name__ == "__main__":
    LISTENING_SOCKET = socket.socket()
    LISTENING_SOCKET.settimeout(0.5)
    IP_ADDRESS = os.getenv("HOST_IP", "127.0.0.1")
    PORT = socket.htons(int(os.getenv("PORT", "7840")))
    print("Starting game server.")
    print("IP = ", IP_ADDRESS)
    print("Port = ", socket.ntohs(PORT))
    if socket.inet_aton(IP_ADDRESS) == 0 or PORT < 1024:
        print("Wrong IP address or port")
        exit(1)
    LISTENING_SOCKET.bind((IP_ADDRESS, PORT))
    LISTENING_SOCKET.listen()
    server.server_main.main(LISTENING_SOCKET)
    LISTENING_SOCKET.close()
