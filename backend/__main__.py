"""
This is client`s backend
"""

import socket
from connection import connection as Conn
from monitor import Monitor

class Common(Monitor):
	"""
	This class consists of common data between backend and interface
	"""
	def __init__(self):
		Monitor.__init__(self)
		self.ip = ""
		self.port = 0
		self.is_master = False

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


if __name__ == "__main__":
	com = Common()
	com.set_connection_params("8.8.8.8", 80)
	com.connect()