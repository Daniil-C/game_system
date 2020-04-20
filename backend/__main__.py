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


class Common(Monitor):
	"""
	This class consists of common data between backend and interface
	"""
	def __init__(self):
		Monitor.__init__(self)
		self.ip = ""
		self.port = 0
		self.player = Player()

	def set_connection_params(self, ip, port):
		"""
		Set connections params to connect to game server
		"""
		self.ip = ip
		self.port = port 

	def connect(self):
		"""
		Connect to the server
		"""
		sock = socket.socket()
		self.conn = Conn(sock)


class Backend(threading.Thread):
	"""
	This class is a backend service of game
	"""
	def __init__(self, common):
		threading.Thread.__init__(self)
		self.common = common

	def start_game(self):
		"""
		Starts the game
		"""
		self.common.connect()





if __name__ == "__main__":
	com = Common()
	com.set_connection_params("8.8.8.8", 80)
	thread = Backend(com)
	thread.start()
	
	time.sleep(1)
	ip, port = thread.get_con_params()
	print("ip: {}, port: {}".format(ip, port))
	thread.join()