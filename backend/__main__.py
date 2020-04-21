"""
This is client`s backend
"""

import socket
import logging
import threading
import time
from connection import connection as Conn
from monitor import Monitor


class Player:
    """
    This class provides players data
    """
    def __init__(self):
        self.cards = []
        self.is_master = False
        self.name = ""


class Common(Monitor):
    """
    This class consists of common data between backend and interface
    """
    def __init__(self):
        Monitor.__init__(self)
        self.ip = ""
        self.port = 0
        self.player = Player()

    def set_ip_port(self, ip, port):
        """
        Set connections params to connect to game server
        """
        self.ip = ip
        self.port = port

    def set_name(self, name):
        """
        Sets player`s name
        """
        self.player.name = name


class Backend(threading.Thread):
    """
    This class is a backend service of game
    """
    def __init__(self, common):
        threading.Thread.__init__(self)
        self.common = common

    def set_connection_params(self, ip, port):
        """
        Set connections params to connect to game server
        """
        self.common.set_ip_port(ip, port)
        logging.debug("Connection params: ip {}, port {}".format(ip, port))
        try:
            self.connect()
            self.sock.close()
            return True
        except Exception as e:
            logging.error("Error while connection: {}".format(e))
            return False

    def connect(self):
        """
        Connect to the server
        """
        self.sock = socket.socket()
        self.sock.connect((self.common.ip, self.common.port))
        self.conn = Conn(self.sock)

    def set_name(self, name):
        """
        Sets player`s name
        """
        logging.info("Hi, {}".format(name))
        self.common.set_name(name)

    def start_game(self):
        """
        Starts the game
        """
        self.connect()
        logging.info("Game started")
        



if __name__ == "__main__":
    logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level=logging.DEBUG)
    com = Common()
    back = Backend(com)
    back.start()
    if back.set_connection_params("localhost", 8000):
        logging.info("Connected succesfully")
        back.set_name("Ivan")
        back.start_game()
    else:
        logging.error("Fail to connect")
    back.join()
