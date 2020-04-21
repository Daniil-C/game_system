"""
This is client`s backend
"""

import socket
import logging
import threading
import time
from connection import connection as Conn
from monitor import Monitor
import interface


class Player:
    """
    This class provides players data
    """
    def __init__(self):
        self.cards = []
        self.is_master = False
        self.name = ""
        self.number = -1


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

    def set_number(self, number):
        """
        Sets player`s number
        """
        self.player.number = number

    def set_master(self):
        """
        Sets player`s master role
        """
        self.player.is_master = True

    def get_name(self):
        """
        Returns player`s name
        """
        return self.player.name

    def get_number(self):
        """
        Returns player`s number
        """
        return self.player.number

    def get_ip_port(self):
        """
        Returns (ip, port)
        """
        return self.ip, self.port

    def is_master(self):
        """
        Returns true if player is a master
        """
        return self.player.is_master


def parse_message(message):
    """
    Parse mmessage by spaces
    """
    return message.split(" ")



class Backend(threading.Thread):
    """
    This class is a backend service of game
    """
    def __init__(self, common):
        threading.Thread.__init__(self)
        self.common = common
        self.version = "res_0.0"

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
        self.conn.send("OK {}".format(self.common.get_name()))

    def set_mode(self, mode):
        """
        Sets game mode
        """
        self.mode = mode


    def start_game(self):
        """
        Starts the game
        """
        self.connect()
        logging.info("Game started")
        mes = self.conn.get()
        logging.debug(mes)
        parsed = parse_message(mes)
        if parsed[0] == "VERSION":
            player_num = int(parsed[1])
            role = parsed[2]
            version = parsed[3]
            url = parsed[4]
            if version != self.version:
                logging.debug("Versions are different")
                # TODO
            if role == "MASTER":
                self.common.set_master()
            self.common.set_number(player_num)




        else:
            raise Exception("Unexpected keyword. Expected: VERSION, real: {}".format(parsed[0]))





if __name__ == "__main__":
    logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level=logging.DEBUG)
    com = Common()
    back = Backend(com)
    back.start()
    interface.init_interface(com, back)
    back.join()
