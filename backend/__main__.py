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
import wget
import os
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
        self.is_leader = False
        


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
        self.game_started = False
        self.mode = ""
        self.turn = False
        self.got_list = False
        self.updated = False
        self.card = 0
        self.ass = ""
        self.got_ass = False

    def reset(self):
        self.player = Player()
        self.players_list = []
        self.game_started = False

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

    def set_player(self):
        """
        Sets player`s master role
        """
        self.player.is_master = False

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
        Returns players list
        """
        return self.players_list

    def get_mode(self):
        """
        Returns game mode
        """
        return self.mode

    def updated(self):
        """
        Returns whether udating is finished
        """
        return self.updated


def parse_message(message, sep):
    """
    Parse mmessage by spaces
    """
    return message.split(sep)


class Backend(Monitor):
    """
    This class is a backend service of game
    """
    def __init__(self, common, in_q):
        Monitor.__init__(self)
        self.common = common
        self.in_q = in_q
        self.version = "res_0.0"
        self.end = False
        self.reader = threading.Thread(target=Backend.read_queue, args=(self,))
        self.reader.start()
        self.game_started = False
        self.begin_message = ""
        self.collector_thread = None
        self.tasks = []
        self.conn = None

        try:
            with open("config.txt", "r") as f:
                s = f.read()
                data = json.loads(s)
                self.common.ip = data["ip"]
                self.common.port = int(data["port"])
                self.common.is_connected = False
        except Exception:
            pass

    def start(self):
        if self.collector_thread is None:
            self.collector_thread = threading.Thread(target=Backend.thr_collector, args=(self,))
            self.collector_thread.start()

    def join(self):
        if self.collector_thread is not None:
            self.collector_thread.join()
            self.collector_thread = None
        else:
            print("No collector thread found!")
        self.stop()

    def thr_collector(self):
        while not self.end:
            time.sleep(2)
            for i in self.tasks:
                if not i.is_alive():
                    i.join()
                    self.tasks.remove(i)
                    break
        for i in self.tasks:
            i.join()

    def queue_request_wrapper(self, fun, args):
        self.__getattribute__(fun)(*args)

    def read_queue(self):
        """
        Reads queue
        """
        while not self.end:
            data = in_q.get()
            logging.debug(data)
            data = json.loads(data)
            if data["method"] == "stop":
                self.end = True
                try:
                    self.conn.send("SHUTDOWN")
                except Exception:
                    pass
                logging.debug("stopping")
            else:
                thread = threading.Thread(target=self.queue_request_wrapper, args=(data["method"], data["args"]))
                thread.start()
                self.tasks.append(thread)

    def stop(self):
        self.end = True
        if self.conn is not None:
            self.conn.close()
        logging.debug("Closing socket")
        self.reader.join()
        logging.debug("Closing reader")
        try:
            self.updater.join()
            logging.debug("Closing updater")
        except Exception as ex:
            logging.error(ex)

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
        self.common.is_connected = True

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
        self.updater.join()
        if self.begin_message:
            self.game()

    def game(self):
        """
        Provides game logic
        """
        self.game_started = True
        self.common.game_started = True
        mes = self.begin_message
        logging.debug(mes)
        parsed = parse_message(mes, " ")
        self.common.mode = parsed[1]
        self.common.player.cards = parse_message(mes[2], ",")
        logging.debug(parsed[3])
        self.common.players_list = [[0, i.split(";")[1]] for i in parse_message(parsed[3], ",")]
        self.game_started = True
        self.common.game_started = True
        self.common.got_list = True
        self.conn.send("READY")
        # Waining TURN from server
        while self.turn():
            pass
        # End game logic; no any connection left.

    def turn(self):            
        mes = self.conn.get()
        logging.debug(mes)
        if "TURN" in mes:
            parsed = parse_message(mes, " ")
            self.common.turn = int(parsed[1]) == self.common.player.number
        else:
            return False
        self.common.got_list = True



    def get_players_list(self):
        """
        Updates players table
        """
        self.sock.settimeout(1)
        while not self.game_started and not self.end:
            try:
                mes = self.conn.get()
                if len(mes) == 0:
                    self.common.is_connected = False
                    break
                logging.debug(mes)
                if "BEGIN" in mes:
                    self.begin_message = mes
                    break
                parsed = parse_message(parse_message(mes, " ")[1], ",")
                logging.debug(parsed[0])
                self.common.players_list = [i.split(";") for i in parsed]
                time.sleep(1)
            except Exception as ex:
                logging.error(ex)
        self.sock.settimeout(None)

    def set_mode(self, mode):
        """
        Sets game mode
        """
        self.common.mode = mode

    def start_game(self):
        """
        Starts the game
        """
        try:
            self.connect()
        except Exception as ex:
            logging.error(ex)
            self.common.is_connected = False
            return
        logging.info("Game started")
        mes = self.conn.get()
        logging.debug(mes)
        if len(mes) == 0:
            self.common.is_connected = False
        parsed = parse_message(mes, " ")
        if parsed[0] == "VERSION":
            player_num = int(parsed[1])
            role = parsed[2]
            version = parsed[3]
            url = parsed[4]
            if version != self.version:
                logging.debug("Versions are different")
                path = os.path.join(os.getcwd(), "resources")
                bar = ""
                filename = wget.download(url, path, bar=bar)
                logging.debug(filename)
                self.common.updated = True
            else:
                self.common.updated = True
            if role == "MASTER":
                self.common.set_master()
            else:
                self.common.set_player()
            self.common.set_number(player_num)
        else:
            raise Exception("Unexpected keyword. "
                            "Expected: VERSION, real: {}".format(parsed[0]))

    def play(self):
        """
        Starts playing
        """
        logging.debug("STARTING GAME")
        self.conn.send("START_GAME {}".format(self.common.mode))


    def exit(self):
        """
        Restarts menu
        """
        self.conn.close()
        self.game_started = False
        try:
            self.updater.join()
        except Exception as ex:
            logging.error(ex)
        self.common.reset()

    def set_card(self, card_num):
        """
        Select card
        """
        self.common.card = card_num

    def set_ass(self,  ass):
        """
        Select association
        """ 
        self.common.ass = ass
        mes = "TURN {} {}".format(self.common.card, self.common.ass)
        self.conn.send(mes)
        logging.debug(mes)


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
        d = {"method": "connect", "args": []}
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
        d = {"method": "start_game", "args": []}
        in_q.put(json.dumps(d))

    def stop(self):
        """
        Stops the game
        """
        d = {"method": "stop", "args": []}
        in_q.put(json.dumps(d))

    def play(self):
        """
        Starts playing
        """
        d = {"method": "play", "args": []}
        in_q.put(json.dumps(d))

    def exit(self):
        """
        Restarts menu
        """
        d = {"method": "exit", "args": []}
        in_q.put(json.dumps(d))

    def set_card(self, card_num):
        """
        Select card
        """
        d = {"method": "set_card", "args": [card_num]}
        in_q.put(json.dumps(d)) 

    def set_ass(self,  ass):
        """
        Select association
        """ 
        d = {"method": "set_ass", "args": [ass]}
        in_q.put(json.dumps(d))



if __name__ == "__main__":
    logging.basicConfig(format=u'[LINE:%(lineno)d]# %(levelname)-8s '
                        '[%(asctime)s]  %(message)s', level=logging.DEBUG)
    com = Common()
    in_q = Queue()
    back = Backend(com, in_q)
    back_int = BackendInterface(in_q)
    back.start()
    interface.init_interface(com, back_int)
    back.join()
    back_int.stop()
