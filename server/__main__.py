"""
Server for Imaginarium game
"""
import socket
import logging
import sys
import server.environment as env
from server.server_main import game_server


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)-15s %(message)s", filename=env.get_log_file())
    LOGGER = logging.getLogger("Game server")
    LOGGER.setLevel("INFO")
    LISTENING_SOCKET = socket.socket()
    LISTENING_SOCKET.settimeout(0.5)
    IP_ADDRESS = env.get_ip()
    PORT = env.get_port()
    LOGGER.info("Starting server. IP: %s Port: %s", IP_ADDRESS, str(PORT))
    print("IP =", IP_ADDRESS)
    print("Port =", PORT)
    print("Resources =", env.get_res_name())
    print("Resources link =", env.get_res_link())
    if socket.inet_aton(IP_ADDRESS) == 0 or PORT < 1024:
        print("Wrong IP address or port")
        sys.exit(1)
    try:
        LISTENING_SOCKET.bind((IP_ADDRESS, PORT))
    except OSError as ex:
        LOGGER.critical("Failed to bind listening socket.")
        LISTENING_SOCKET.close()
        sys.exit(2)
    LISTENING_SOCKET.listen()
    SERVER = game_server(LISTENING_SOCKET, LOGGER)
    SERVER.main()
    LISTENING_SOCKET.close()
    LOGGER.info("Shutdown.")
