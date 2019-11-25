import random
import Pyro4
from threading import Thread
import threading
import time


m = 8
M = (1 << m) -1

node_uri = 'chord.node.%s'


def info(msg:str):
    print(msg)

def repeat(sleep_time, condition : lambda *args: True):
	def decorator(func):
		def inner( *args, **kwargs):
			while condition(*args):
				func( *args, **kwargs)
				time.sleep(sleep_time)
		return inner
	return decorator

def in_interval(x: int, a: int, b: int) -> bool:
    return  a < x < b if a > b else x > a or x < b

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

    def awake(self,node):
        if not node:
            node = self
        #info('starting Pyro daemon...')
        Thread(target=self.pyro_daemon.requestLoop, daemon=True).start()
        #info('finding pyro name server...')
        with Pyro4.locateNS() as ns:
            ns.register(node_uri % self.id,self.uri, metadata=['chord-node'])
        #with Pyro4.Proxy('pyrometa:chord-node') as node:
        #   node.id
        self.join(node)
        #info('looking for random node...')
        
        self.alive = True
        #Thread(target=self.fix_fingers, daemon=True).start()
        Thread(target=self.stabilize, daemon=True).start()
        
        
    def __del__(self):
        self.alive = False
        self.pyro_daemon.close()

    # node self joins the network
    # 'node' is a arbitrary node in the network
    def join(self, node: 'Node'):
        info(f'Node {self.id} joining using Node {node.id}')
        self.predecessor = None
        self.successor =  self if self.id == 0 else node.find_successor(self.id)


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
        if id == self.id:  
            return self
        
        node = self
        while not in_interval_r(id,node.id,node.successor.id):
            node = node.closet_preceding_finger(id)
            info(f'find predecessor in Node {self.id} : not {node.id}<{id}<={node.successor.id}')
        return node

    # return closest finger preceding id
    def closet_preceding_finger(self, id: int) -> 'Node':
        self.finger.print_fingers()
        for i in range(m-1, 0,-1):
            info(f'index: {i}')
            finger_successor = self.finger[i].successor
            if finger_successor>-1 and in_interval(finger_successor,self.id,id):
                return self.finger[i].node
        return self


    # periodically verify self's inmediate succesor and tell the successor about self
    @repeat(0.1,lambda *args: args[0].alive)
    def stabilize(self):
        
        node = self.successor.predecessor
        #info(f"Node {self.id} stabilize with Node {node.id if node else 'None'}")
        if node and (in_interval_r(node.id,self.id,self.successor.id) or self.id == self.successor.id):
            self.successor = node
        self.successor.notify(self)

    # node think is might be our predecessor
    def notify(self, node: 'Node'):
        if not self.predecessor or in_interval(node.id,self.predecessor.id,self.id): #TODO: check why is this code wrong
            self.predecessor = node

    @repeat(0.1,lambda *args: args[0].alive)
    # periodically refresh finger table entries
    def fix_fingers(self):
        #info("fixing fingers...")
        i = random.randrange(1, m)
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
            info(f'Node {self.id} find key {key}')
            return self.data[key]
        node = self.find_successor(key)
        return node.find(key)
        
    def belong(self, key: int):
        return in_interval(key, self.predecessor.id, self.id)
    # end Node


class Finger:
    def __init__(self, start, interval, successor):
        self.start = start
        self.interval = interval
        self.successor = successor

    @property
    def node(self):
        info('requering finger node')
        node = Pyro4.Proxy(f"PYRONAME:{node_uri % self.successor}")
        return node


class FingerTable:
    def __init__(self, id):
        self.id = id
        self.fingers = []
        for i in range(m):
            start = self.fix(i)
            self.fingers.append(Finger(start, None, -1))
        self.print_fingers()
        
    def print_fingers(self):
        info(list(map(lambda f:f.successor, self.fingers)))    

    def __getitem__(self, index):  # get node at this position
        return self.fingers[index]

    def __setitem__(self, index, value: 'Node'):  # get node at this position
        self.print_fingers()
        start = self.fix(index)
        self.fingers[index] = Finger(start, None, value.id)
        self.print_fingers() 

    def fix(self, k):
        info(f'k = {k}, 2**(k-1)= {1 << (k)}')
        return (self.id + 1 << k) % M  # return the id of the given index of this finger table

import sys
nodes = []
for i in range(3):
    nodes.append(Node(i,f'127.0.0.{1+i}',9971+i))
    nodes[i].awake(nodes[i-1] if i>0 else None)             

node  = nodes[0]
time.sleep(1)
for n in range(len(nodes)):
    print(f'Node {n} have succesor: {nodes[n].successor.id}')
    print(f'Node {n} have predecessor: {nodes[n].predecessor.id}')
'''node.storage(5,"esto debe estar en Nodo 6")
node.storage(3,"esto debe estar en Nodo 4")'''
'''info(node.find(5))
info(node.find(3))'''