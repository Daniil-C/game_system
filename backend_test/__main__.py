""" Testing module for backend"""
import logging
import threading
import time
from multiprocessing import Queue
import json
import os
import sys
import shutil
#import wget
import interface
from zipfile import ZipFile
from monitor import Monitor
from backend import Backend, BackendInterface, Player, Common

class socket:
    """ Mocking socket """
    def __init__(self):
        """ init """
        pass

    def settimeout(timeout=None):
        """ settimeout """
        pass

    def close(self):
        """ close """
        pass

class Conn:
    """ Mocking class for Conn """
    def __init__(self):
        self.__in_q = self.Get()

    def send(message):
        print(mes)

    def Get(self):
        yield "VERSION 0 MASTER v0 http://pack.zip"
        yield "PLAYER_LIST 0;qwer"

    def get(self):
        try:
            return next(self.__in_q)
        except:
            return ""

    def close(self):
        print("close")

class Backend(Backend):
    """ Change methods for testing"""
    def connect(self, timeout=None):
        """ Connect to the server """
        print(dir())
        self.conn = Conn()
        self.common.is_connected = True

    def update(self, cwd, url):
        """
        Updates res
        """
        for i in range(5):
            self.common.coef = i / 5
            time.sleep(1)

if __name__ == "__main__":
    logging.basicConfig(format=u'[LINE:%(lineno)d]# %(levelname)-8s '
                        '[%(asctime)s]  %(message)s', level=logging.DEBUG)
    os.environ["CONFIG"] = "/tmp/conf.json"
    with open(os.environ["CONFIG"], "w") as f:
        f.write("{'version': 'v1', 'ip': '8.8.8.8', 'port':'1234'}")
    com = Common()
    in_q = Queue()
    back = Backend(com, in_q)
    back_int = BackendInterface(in_q)
    back.start()
    interface.init_interface(com, back_int)
    back.join()
    back_int.stop()