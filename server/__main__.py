"""
Server for Imaginarium game
"""
import socket
import server.environment as env
import server.server_main


if __name__ == "__main__":
    LISTENING_SOCKET = socket.socket()
    LISTENING_SOCKET.settimeout(0.5)
    IP_ADDRESS = env.get_ip()
    PORT = env.get_port()
    print("Starting game server.")
    print("IP =", IP_ADDRESS)
    print("Port =", PORT)
    print("Resources =", env.get_res_link())
    if socket.inet_aton(IP_ADDRESS) == 0 or PORT < 1024:
        print("Wrong IP address or port")
        exit(1)
    LISTENING_SOCKET.bind((IP_ADDRESS, PORT))
    LISTENING_SOCKET.listen()
    server.server_main.main(LISTENING_SOCKET)
    LISTENING_SOCKET.close()
