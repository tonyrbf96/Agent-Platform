import random
import Pyro4
from threading import Thread
import threading
import time

m = 7
M = (1 << m) - 1

node_uri = 'chord.node.%s'


def info(msg: str):
    print(msg)


def repeat(sleep_time, condition: lambda *args: True):
    def decorator(func):
        def inner(*args, **kwargs):
            while condition(*args):
                func(*args, **kwargs)
                time.sleep(sleep_time)
        return inner
    return decorator

# 0 entre 10 y 6
def in_interval(x: int, a: int, b: int) -> bool:
    return a < x < b if a < b else not b <= x <=a


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

    def awake(self, node):
        if not node:
            node = self
        Thread(
            target=self.pyro_daemon.requestLoop,
            daemon=True).start()
        with Pyro4.locateNS() as ns:
            ns.register(
                node_uri %
                self.id,
                self.uri,
                metadata=['chord-node'])
        self.join(node)

        self.alive = True
        Thread(target=self.fix_fingers, daemon=True).start()
        Thread(target=self.stabilize, daemon=True).start()

    def shutdown(self):

        self.alive = False
        self.pyro_daemon.close()

    def join(self, node: 'Node'):
        "node self joins the network node is a arbitrary node in the network"
        self.predecessor = None
        self.successor = self if self.id == 0 else node.find_successor(
            self.id)

    @property
    def id(self):
        return self.__id

    @id.setter
    def id(self, value):
        self.__id = value

    # sefl's successor
    @property
    def successor(self) -> 'Node':
        return self.finger[0].node

    @successor.setter
    def successor(self, value):
        self.finger[0] = value

    @property
    def predecessor(self) -> 'Node':
        "Node predecessor, it is a life time proxy"
        return self.__predecessor

    @predecessor.setter
    def predecessor(self, value):
        "Node predecessor, it is a life time proxy"
        self.__predecessor = value

    def find_successor(self, id: int) -> 'Node':
        "Find id's successor in Ring"
        p = self.find_predeccessor(id)
        return p.successor

    def find_predeccessor(self, id: int) -> 'Node':
        "Find id's precessor in Ring"
        if id == self.id:
            return self

        node = self
        while not in_interval_r(id, node.id, node.successor.id):
            node = node.closet_preceding_finger(id)
        return node

    def closet_preceding_finger(self, id: int) -> 'Node':
        "Return closest finger preceding this id"
        for i in range(m - 1, -1, -1):
            if self.finger[i].id and in_interval(
                    self.finger[i].id, self.id, id):
                return self.finger[i].node
        return self

    @repeat(0.25, lambda *args: args[0].alive)
    def stabilize(self):
        "Periodically verify node's inmediate succesor and tell the successor about it"

        node = self.successor.predecessor
        if node and in_interval_r(node.id, self.id, self.successor.id):
            self.successor = node
        self.successor.notify(self)

    def notify(self, node: 'Node'):
        "Node think is might be our predecessor"
        if not self.predecessor or in_interval(
                node.id, self.predecessor.id, self.id):  # TODO: check why is this code wrong
            self.predecessor = node
            node_id = node.id
            # Transfer data to predecessor
            # info(f"Node {self.id} has data: {self.data}\n")
            pred_data = dict(
                filter(
                    lambda i: i[0] < self.predecessor.id,
                    self.data.items()))
            # info(f"Node {self.id} send: {pred_data} to node {node_id}\n")
            # remove transfering data from node data
            self.data = {
                k: v for k,
                v in self.data.items() if k not in pred_data}
            # info(f"Node {self.id} has data: {self.data}\n")
            # send data to predecessor node
            self.predecessor.set_data(pred_data)

    @repeat(0.25, lambda *args: args[0].alive)
    def fix_fingers(self):
        "Periodically refresh finger table entries"
        i = random.randrange(1, m)
        # if self.id==90: info(f'Fixing fingers at  {i} and adding successor of {self.finger[i].start} result in {self.find_successor(self.finger[i].start)} ')
        self.finger[i] = self.find_successor(self.finger[i].start)

    def set_data(self, data):
        "This is used for the successor node for transfer the correspondent data"
        self.data = {**self.data, **data}

    def save(self, key: int, value):
        node = self.find_successor(key)
        node.set_item(key, value)

    def set_item(self, key, value):
        self.data[key] = value

    def load(self, key):
        node = self.find_successor(key)
        return node.get_item(key)

    def get_item(self, key):
        return self.data[key] if self.data.__contains__(key) else None

    # def belong(self, key: int):
    #     'Do not use this, predecessor needed'
    #     return in_interval(key, self.predecessor.id, self.id)

    def print_info(self):
        info('==================')
        info(f'Node: {self.id}')
        info(f'suc: {self.successor.id if self.successor else None}')
        info(
            f'pred: {self.predecessor.id if self.predecessor else None}')
        info(f'finger: {self.finger.print_fingers()}')
        info(f'data: {self.data}')
        info('==================')
    # end Node


class Finger:
    def __init__(self, start, interval, id):
        self.start = start
        self.interval = interval
        self.id = id

    @property
    def node(self):
        node = Pyro4.Proxy(f"PYRONAME:{node_uri % self.id}")
        return node


class FingerTable:
    def __init__(self, id):
        self.id = id
        self.fingers = []
        for i in range(m):
            start = self.fix(i)
            self.fingers.append(Finger(start, None, None))

    def print_fingers(self):
        return list(
            map(lambda f: f'{f.start}:{f.id}', self.fingers))

    def __getitem__(self, index):  # get node at this position
        return self.fingers[index]

    def __setitem__(self, index, value: 'Node'):  # get node at this position
        start = self.fix(index)
        self.fingers[index] = Finger(start, None, value.id)

    def fix(self, k):
        return (self.id + (1 << k)) % M


if __name__ == "__main__": 
    nodes = []


    def print_all():
        for n in nodes:
            n.print_info()

    print(in_interval(30,30,0 ))
    for i in range(7):
        nodes.append(
            Node(
                0 if i == 0 else i * 10,
                f'127.0.0.{1+i}',
                9971 + i))
        nodes[i].awake(nodes[i - 1] if i > 0 else None)
        time.sleep(.5)
        for d in range(5):
            nodes[i].save(i * 10 + 1+d, '')



    time.sleep(10)
    for n in range(len(nodes)):
        nodes[n].print_info()

    # info(node.load(14))
    # info(node.load(65))
