import random
import Pyro4
import logging
from threading import Thread
import threading
import time


m = 8
M = 2 ** m

node_uri = 'chord.node.%s'


def info(msg:str):
    print(msg)

def repeat(sleep_time, condition : lambda *args: True):
	def decorator(func):
		def inner( *args, **kwargs):
			while condition(*args):
				time.sleep(sleep_time)
				func( *args, **kwargs)
		return inner
	return decorator

def in_interval(x: int, a: int, b: int) -> bool:
    return  x==a and x==b or a < x < b if a > b else x > a or x < b

def in_interval_r(x: int, a: int, b: int) -> bool:
    return in_interval(x, a, b) or x == b

def in_interval_l(x: int, a: int, b: int) -> bool:
    return in_interval(x, a, b) or x == a

@Pyro4.expose
class Node:
    def __init__(self, id, ip, port):
        self.id = id
        print(f'Node id: {self.id}')
        self.ip = ip
        self.port = port
        self.finger = FingerTable(self.id)
        self.data = {}
        self.pyro_daemon = Pyro4.Daemon(host=self.ip, port=self.port)
        self.uri = self.pyro_daemon.register(self, node_uri % self.id)

    def start(self):
        info('starting Pyro daemon...')
        Thread(target=self.pyro_daemon.requestLoop, daemon=True).start()
        info('finding pyro name server...')
        with Pyro4.locateNS() as ns:
            ns.register(node_uri % self.id,self.uri, metadata=['chord-node'])
        
        info('looking for random node...')
        node = self #TODO find node in name server
        self.join(node)
        
        self.alive = True
        Thread(target=self.fix_fingers, daemon=True).start()
        Thread(target=self.stabilize, daemon=True).start()
        
        
    def __del__(self):
        self.alive = False
        self.pyro_daemon.close()

    # node self joins the network
    # 'node' is a arbitrary node in the network
    def join(self, node: 'Node'):
        info(f'joining from {node.id}')
        self.predecessor = None
        self.successor = node.find_successor(self.id)


    @property
    def id(self):
        return self.__id
    
    @id.setter
    def id(self,value):
        self.__id = value

    # sefl's successor
    @property
    def successor(self) -> 'Node':
        return self.finger[0].node

    @successor.setter
    def successor(self, value):
        self.finger[0] = value

    # sefl's successor
    @property
    def predecessor(self) -> 'Node':
        return self.__predecessor

    @predecessor.setter
    def predecessor(self, value):
        self.__predecessor = value

    # ask node self to find id's successor
    def find_successor(self, id: int) -> 'Node':
        p = self.find_predeccessor(id)
        return p.successor

    # ask node self to find id's precessor
    def find_predeccessor(self, id: int) -> 'Node':
        node = self
        while node.id < id <= node.successor.id:
            node = node.closet_preceding_finger(id)  # RPC call
        return node

    # return closest finger preceding id
    def closet_preceding_finger(self, id: int) -> 'Node':
        for i in range(M, 1):
            if self.id < self.finger[i].id < id:
                return self.finger[i]
        return self


    # periodically verify self's inmediate succesor and tell the successor about self
    @repeat(0.5,lambda *args: args[0].alive)
    def stabilize(self):
        #info("stabilizing...")
        node = self.successor.predecessor
        if node and self.id < node.id < self.successor.id:
            self.successor = node
        self.successor.notify(self)

    # node think is might be our predecessor
    def notify(self, node: 'Node'):
        if not self.predecessor or self.predecessor.id < node.id < self.id:
            self.predecessor = node

    @repeat(0.5,lambda *args: args[0].alive)
    # periodically refresh finger table entries
    def fix_fingers(self):
        #info("fixing fingers...")
        i = random.randrange(0, m)
        self.finger[i] = self.find_successor(self.finger[i].start)

        # Data

    def storage(self, key: int, value):
        if self.belong(key):
            self.data[key] = value
            return
        node = self.find_successor(key)
        node.storage(key, value)

    def find(self,key):
        if self.belong(key):
            return self.data[key]
        node.self.find_successor(key)
        return node.find(key)
        
    def belong(self, key: int):
        return in_interval(key, self.predecessor.id, self.id)
    # end Node


class Finger:
    def __init__(self, start, interval, succesor):
        self.start = start
        self.interval = interval
        self.succesor = succesor

    @property
    def node(self):
        node = Pyro4.Proxy(f"PYRONAME:{node_uri % self.succesor}")
        return node


class FingerTable:
    def __init__(self, id):
        self.id = id
        self.fingers = []
        for i in range(m):
            start = self.fix(i)
            self.fingers.append(Finger(start, None, self.id))
        

    def __getitem__(self, index):  # get node at this position
        return self.fingers[index]

    def __setitem__(self, index, value: 'Node'):  # get node at this position
        start = self.fix(index)
        self.fingers[index] = Finger(start, None, value.id) if value else None

    def fix(self, k):
        return (self.id + 2 ** (k - 1)) % M  # return the id of the given index of this finger table

node  = Node(1,'localhost',9999)
node.start()
time.sleep(10)