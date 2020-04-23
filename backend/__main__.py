"""
This is client`s backend
"""

import socket
import logging
import threading
import time
from multiprocessing import Queue
import interface
import json
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
        self.number = -1


class Common(Monitor):
    """
    This class consists of common data between backend and interface
    """
    def __init__(self):
        Monitor.__init__(self)
        self.ip = ""
        self.port = 0
        self.is_connected = False
        self.player = Player()
        self.players_list = []

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

    def get_players_list(self):
        """
        Returns (ip, port)
        """
        return self.players_list


def parse_message(message, sep):
    """
    Parse mmessage by spaces
    """
    return message.split(sep)


class Backend(threading.Thread):
    """
    This class is a backend service of game
    """
    def __init__(self, common, in_q):
        threading.Thread.__init__(self)
        self.common = common
        self.in_q = in_q
        self.version = "res_0.0"
        self.end = 0
        self.reader = threading.Thread(target=Backend.read_queue, args=(self,))
        self.reader.start()
        self.game_started = False

        try:
            with open("config.txt", "r") as f:
                s = f.read()
                data = json.loads(s)
                self.common.ip = data["ip"]
                self.common.port = int(data["port"])
        except Exception:
            pass

    def read_queue(self):
        """
        Reads queue
        """
        while not self.end:
            data = in_q.get()
            logging.debug(data)
            data = json.loads(data)
            if data["method"] == "stop":
                self.end = 1
            else:
                if data["args"] is not None:
                    args = data["args"]
                    self.__getattribute__(data["method"])(*args)
                else:
                    self.__getattribute__(data["method"])()

    def stop(self):
        self.conn.close()
        self.reader.join()

    def set_connection_params(self, ip, port):
        """
        Set connections params to connect to game server
        """
        self.common.set_ip_port(ip, port)
        logging.debug("Connection params: ip {}, port {}".format(ip, port))
        try:
            self.connect(10)
            self.sock.close()
            self.common.is_connected = True
            with open("config.txt", "w") as f:
                data = {"ip": ip, "port": port}
                f.write(json.dumps(data))
        except Exception as e:
            logging.error("Error while connection: {}".format(e))
            self.common.is_connected = False

    def connect(self, timeout=None):
        """
        Connect to the server
        """
        self.sock = socket.socket()
        self.sock.settimeout(timeout)
        self.sock.connect((self.common.ip, self.common.port))
        self.conn = Conn(self.sock)

    def set_name(self, name):
        """
        Sets player`s name
        """
        logging.info("Hi, {}".format(name))
        self.common.set_name(name)
        self.conn.send("OK {}".format(self.common.get_name()))
        self.updater = threading.Thread(target=Backend.get_players_list,
                                        args=(self,))
        self.updater.start()

    def get_players_list(self):
        """
        Updates players table
        """
        self.sock.settimeout(1)
        while not self.game_started:
            try:
                mes = self.conn.get()
                logging.debug(mes)
                parsed = parse_message(mes, ",")
                self.common.players_list = [i.split(";") for i in parsed]
            except Exception:
                pass
        self.sock.settimeout(None)

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
        parsed = parse_message(mes, " ")
        if parsed[0] == "VERSION":
            player_num = int(parsed[1])
            role = parsed[2]
            version = parsed[3]
            # url = parsed[4]
            if version != self.version:
                logging.debug("Versions are different")
                # TODO
            if role == "MASTER":
                self.common.set_master()
            self.common.set_number(player_num)
        else:
            raise Exception("Unexpected keyword. "
                            "Expected: VERSION, real: {}".format(parsed[0]))

    def play(self):
        """
        Starts playing
        """
        self.game_started = True
        self.updater.join()
        self.conn.send("START_GAME {}".format(self.mode))

    def exit(self):
        """
        Restarts menu
        """
        self.conn.close()


class BackendInterface:
    """
    This class provides interface between frondtend and backend
    """
    def __init__(self, in_q):
        threading.Thread.__init__(self)
        self.in_q = in_q

    def set_connection_params(self, ip, port):
        """
        Set connections params to connect to game server
        """
        d = {"method": "set_connection_params", "args": [ip, port]}
        in_q.put(json.dumps(d))

    def connect(self):
        """
        Connect to the server
        """
        d = {"method": "connect", "args": None}
        in_q.put(json.dumps(d))

    def set_name(self, name):
        """
        Sets player`s name
        """
        d = {"method": "set_name", "args": [name]}
        in_q.put(json.dumps(d))

    def set_mode(self, mode):
        """
        Sets game mode
        """
        d = {"method": "set_mode", "args": [str(mode)]}
        in_q.put(json.dumps(d))

    def start_game(self):
        """
        Starts the game
        """
        d = {"method": "start_game", "args": None}
        in_q.put(json.dumps(d))

    def stop(self):
        """
        Stops the game
        """
        d = {"method": "stop", "args": None}
        in_q.put(json.dumps(d))

    def play(self):
        """
        Starts playing
        """
        d = {"method": "play", "args": None}
        in_q.put(json.dumps(d))

    def exit(self):
        """
        Restarts menu
        """
        d = {"method": "exit", "args": None}
        in_q.put(json.dumps(d))


if __name__ == "__main__":
    logging.basicConfig(format=u'[LINE:%(lineno)d]# %(levelname)-8s '
                        '[%(asctime)s]  %(message)s', level=logging.DEBUG)
    com = Common()
    in_q = Queue()
    back = Backend(com, in_q)
    back_int = BackendInterface(in_q)
    back.start()
    # back_int.set_connection_params("192.168.1.4", 7840)
    # back_int.connect()
    # back_int.start_game()
    # back_int.set_name("Yar")
    # back_int.set_mode("Ariadna")
    # time.sleep(5)
    # back_int.play()
    # q.close()
    # q.join_thread()
    interface.init_interface(com, back_int)
    # time.sleep(30)
    back_int.stop()
    back.stop()
    back.join()
