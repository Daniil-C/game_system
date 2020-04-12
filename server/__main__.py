"""
Server for Imaginarium game
"""
import socket
import server.environment as env
import server.server_main
import logging


if __name__ == "__main__":
    logging.basicConfig(format="%(asctime)-15s %(message)s", filename="log.txt")
    LOGGER = logging.getLogger("Game server")
    LOGGER.setLevel("INFO")
    LISTENING_SOCKET = socket.socket()
    LISTENING_SOCKET.settimeout(0.5)
    IP_ADDRESS = env.get_ip()
    PORT = env.get_port()
    LOGGER.info("Starting server. IP: " + IP_ADDRESS + " Port: " + str(PORT))
    print("IP =", IP_ADDRESS)
    print("Port =", PORT)
    print("Resources =", env.get_res_link())
    if socket.inet_aton(IP_ADDRESS) == 0 or PORT < 1024:
        print("Wrong IP address or port")
        exit(1)
    try:
        LISTENING_SOCKET.bind((IP_ADDRESS, PORT))
    except Exception as ex:
        LOGGER.critical("Failed to bind listening socket.")
        quit()
    LISTENING_SOCKET.listen()
    server.server_main.main(LISTENING_SOCKET, LOGGER)
    LISTENING_SOCKET.close()
