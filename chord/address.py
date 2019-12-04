import hashlib
from chord.node import Node
#this is for contain ip,port in a object
class Address:
	def __init__(self, ip:str, port:int):
		self.ip = ip
		self.port = port

	def __hash__(self):
		s = "%s:%s".format(self.ip, self.port).encode()
		h = int(hashlib.sha1(s).hexdigest(),16)%chord_settings.MAX_NO_KEYS
		return h

	def __cmp__(self, other):
		return other.__hash__() < self.__hash__()

	def __eq__(self, other):
		return other.__hash__() == self.__hash__()

	def __str__(self):
		return "[\"%s\", %s]" % (self.ip, self.port)
