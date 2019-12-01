
import random
import Pyro4
from threading import Thread
import threading
import time

m = 7
M = (1 << m) - 1


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
    return a < x < b if a < b else not b <= x <= a


def in_interval_r(x: int, a: int, b: int) -> bool:
    return in_interval(x, a, b) or x == b


def in_interval_l(x: int, a: int, b: int) -> bool:
    return in_interval(x, a, b) or x == a


def proxy(node: 'NodeInfo'):
    'Pyro Proxy to that node'
    return Pyro4.Proxy(Node.URI(node.id, node.ip, node.port))


@Pyro4.expose
class Node:
    def __init__(self, id, ip, port):
        self.id = id
        self.ip = ip
        self.port = port
        self.finger = FingerTable(self.id)
        self.data = {}
        self.pyro_daemon = Pyro4.Daemon(host=self.ip, port=self.port)

    def start_serving(self, node: 'NodeInfo' = None):
        '''
        node: Joint point
        '''
        self.pyro_daemon.register(self, Node.Name(self.id))
        Thread(
            target=self.pyro_daemon.requestLoop,
            daemon=True).start()

        if node:
            self.join(node)
        else:
            self.predecessor = None
            self.successor = self.info

        self.alive = True
        Thread(target=self.fix_fingers, daemon=True).start()
        Thread(target=self.stabilize, daemon=True).start()

    def shutdown(self):
        self.alive = False
        self.pyro_daemon.close()

    def join(self, node: 'NodeInfo'):
        "node self joins the network node is a arbitrary node in the network"
        self.predecessor = None
        with proxy(node) as remote:
            self.successor = remote.find_successor(self.id)

    @property
    def successor(self) -> 'NodeInfo':
        return self.finger[0].node

    @successor.setter
    def successor(self, value: 'NodeInfo'):
        self.finger[0] = value

    @property
    def predecessor(self) -> 'NodeInfo':
        "Node predecessor, it is a life time proxy"
        return self.__predecessor

    @predecessor.setter
    def predecessor(self, value: 'NodeInfo'):
        "Node predecessor, it is a life time proxy"
        self.__predecessor = value

    @property
    def info(self):
        return NodeInfo(self.id, self.ip, self.port)

    def find_successor(self, id: int) -> 'NodeInfo':
        "Find id's successor if Ring"
        node = self.find_predeccessor(id)
        with proxy(node) as remote:
            return remote.successor

    def find_predeccessor(self, id: int) -> 'NodeInfo':
        "Find id's precessor in Ring"
        if id == self.id:
            return self.info

        node = self.info
        node_successor = self.successor

        while not in_interval_r(id, node.id, node_successor.id):
            with proxy(node) as remote:
                node = remote.closet_preceding_finger(id)
                node_successor = remote.successor
        return node

    def closet_preceding_finger(self, id: int) -> 'NodeInfo':
        "Return closest finger preceding this id"
        for i in range(m - 1, -1, -1):
            if self.finger[i].node and in_interval(
                    self.finger[i].id, self.id, id):
                return self.finger[i].node
        return self

    @repeat(0.25, lambda *args: args[0].alive)
    def stabilize(self):
        "Periodically verify node's inmediate succesor and tell the successor about it"
        with proxy(self.successor) as remote:
            node = remote.predecessor
            if node and in_interval_r(
                    node.id, self.id, self.successor.id):
                self.successor = node
            remote.notify(self.info)

    def notify(self, node: 'NodeInfo'):
        "Node think is might be our predecessor"
        if not self.predecessor or in_interval(
                node.id, self.predecessor.id, self.id):  # TODO: check why is this code wrong
            self.predecessor = node
            # Transfer data to predecessor
            pred_data = dict(
                filter(
                    lambda i: i[0] < self.predecessor.id,
                    self.data.items()))
            # remove transfering data from node data
            self.data = {
                k: v for k,
                v in self.data.items() if k not in pred_data}
            # send data to predecessor node
            with proxy(self.predecessor) as remote:
                remote.set_data(pred_data)

    @repeat(0.25, lambda *args: args[0].alive)
    def fix_fingers(self):
        "Periodically refresh finger table entries"
        i = random.randrange(1, m)
        self.finger[i] = self.find_successor(self.finger[i].start)

    def set_data(self, data):
        "This is used for the successor node for transfer the correspondent data"
        self.data = {**self.data, **data}

    def save(self, key: int, value):
        node = self.find_successor(key)
        with proxy(node) as remote:
            remote.set_item(key, value)

    def set_item(self, key, value):
        self.data[key] = value

    def load(self, key):
        node = self.find_successor(key)
        with proxy(node) as remote:
            return remote.get_item(key)

    def get_item(self, key):
        return self.data[key] if self.data.__contains__(key) else None

    # def belong(self, key: int):
    #     'Do not use this, predecessor needed'
    #     return in_interval(key, self.predecessor.id, self.id)

    def print_info(self):
        info(f'========  Node: {self.id}  =========')

        info(f'suc: {self.successor.id if self.successor else None}')
        info(f'pred: {self.predecessor.id if self.predecessor else None}')

        info(f'finger: {self.finger.print_fingers()}')
        info(f'data: {self.data}')
        info('========= END =========')

    @staticmethod
    def URI(id: int, ip: str, port: int) -> str:
        return f"Pyro:{Node.Name(id)}@{ip}:{port}"

    @staticmethod
    def Name(id: int) -> str:
        return f'ChordNode-{id}'


######################################################################
class NodeInfo:
    'Represent a ChordNode information necesary to create proxies'

    def __init__(self, id: int, ip: str, port: int):
        self.id = id
        self.ip = ip
        self.port = port


class Finger:
    def __init__(self, start, node):
        self.start = start
        self.node = node

    def set(self, id, ip, port):
        self.id = id
        self.ip = ip
        self.port = port

    @property
    def id(self):
        return self.node.id


class FingerTable:

    def __init__(self, id):
        self.id = id
        self.fingers = []
        for i in range(m):
            start = self.fix(i)
            self.fingers.append(Finger(start, None))

    def print_fingers(self):
        return list(
            map(lambda f: f'{f.start}:{f.id}', self.fingers))

    def __getitem__(self, index: int) -> 'Finger':  # get node at this position
        return self.fingers[index]

    def __setitem__(self, index: int, node: 'NodeInfo'):  # get node at this position
        start = self.fix(index)
        self.fingers[index] = Finger(start, node)

    def fix(self, k):
        return (self.id + (1 << k)) % M


######################################################################

Pyro4.config.SERIALIZER = 'pickle'
Pyro4.config.SERIALIZERS_ACCEPTED = {
    'serpent', 'json', 'marshal', 'pickle'}

nodes = []


def print_all():
    for n in nodes:
        n.print_info()


node_info = None

for i in range(7):
    nodes.append(
        Node(
            i * 10,
            f'127.0.0.{1+i}',
            9990 + i))
    nodes[i].start_serving(node_info)
    node_info = nodes[i].info
    time.sleep(.2)


for i in range(100):
    r = int(random.randrange(127))
    node = nodes[int(r / 20)]
    node.save(r if r % 10 != 0 else r + 1, '')


time.sleep(4)
for n in range(len(nodes)):
    nodes[n].print_info()

# info(node.load(14))
# info(node.load(65))
