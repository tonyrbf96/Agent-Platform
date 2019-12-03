
import random
import Pyro4
from threading import Thread
import threading
import time
m = 7
M = (1 << m) - 1


Pyro4.config.SERIALIZER = 'pickle'
Pyro4.config.SERIALIZERS_ACCEPTED = {
    'serpent', 'json', 'marshal', 'pickle'}

STABILIZATION_TIME = 0.2
RETRY_TIME = STABILIZATION_TIME * 4
ASSURED_LIFE_TIME = RETRY_TIME * 4


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


def retry_if_failure(retry_delay: float, attempts: int = 3):
    'retry call this funtion awating and give hope to in stabilization '
    def decorator(func):
        def inner(*args, **kwargs):
            for i in range(attempts):
                try:
                    result = func(*args, **kwargs)
                except BaseException as error:
                    info(
                        f'retry {i+1}/{attempts} {func.__name__} -> error: {error}')
                    time.sleep(retry_delay)
                    continue
                return result
            raise Exception('fail retry')
        return inner
    return decorator

# 0 entre 10 y 6


def in_interval(x: int, a: int, b: int) -> bool:
    return a < x < b if a < b else not b <= x <= a


def in_interval_r(x: int, a: int, b: int) -> bool:
    return in_interval(x, a, b) or x == b


def proxy(node: 'NodeInfo'):
    'Pyro Proxy to that node'
    return Pyro4.Proxy(Node.URI(node.id, node.ip, node.port))


def is_alive(node: 'NodeInfo'):
    try:
        with proxy(node) as remote:
            remote.ping()
            return True
    except Pyro4.errors.CommunicationError:
        return False


@Pyro4.expose
class Node:
    def __init__(self, id, ip, port):
        self.id = id
        self.ip = ip
        self.port = port
        self.finger = FingerTable(self.id)
        self.data = {}
        self._successor_list = [None for _ in range(m)]
        self.assured_data = {}

    def start_serving(self, node: 'NodeInfo' = None, loop=False):
        '''
        node: Joint point
        '''
        self.pyro_daemon = Pyro4.Daemon(host=self.ip, port=self.port)
        self.pyro_daemon.register(self, Node.Name(self.id))
        Thread(
            target=self.pyro_daemon.requestLoop,
            daemon=True).start()

        if node and node.id != self.id:
            self.join(node)
        else:
            self.predecessor = None
            self.successor = self.info

        Thread(target=self.fix_fingers, daemon=True).start()
        Thread(target=self._stabilize, daemon=True).start()
        Thread(
            target=self._stabilize_successor_list,
            daemon=True).start()
        Thread(
            target=self._stabilize_ensuded_data,
            daemon=True).start()

        info(f"Node {self.id} is ready")

    def __del__(self):
        print(self.__dict__)
        self.pyro_daemon.close()

    @retry_if_failure(RETRY_TIME)
    def join(self, node: 'NodeInfo'):
        "node self joins the network node is a arbitrary node in the network"
        self.predecessor = None
        with proxy(node) as remote:
            self.successor = remote.find_successor(self.id)
            # initialize successor_list using successor.successor_list
            print(self.successor)
            self._update_successor_list()

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

    @property
    def successor_list(self):
        return self._successor_list

    @retry_if_failure(RETRY_TIME)
    def find_successor(self, id: int) -> 'NodeInfo':
        "Find id's successor if Ring"
        node = self.find_predeccessor(id)
        with proxy(node) as remote:
            return remote.successor

    @retry_if_failure(RETRY_TIME)
    def find_predeccessor(self, id: int) -> 'NodeInfo':
        "Find id's precessor in Ring"
        if id == self.id:
            return self.info

        node = self.info
        node_successor = self.successor

        while not in_interval_r(id, node.id, node_successor.id):
            with proxy(node) as remote:
                node = remote.closet_preceding_finger(id)
            with proxy(node) as remote:
                node_successor = remote.successor
        return node

    @retry_if_failure(RETRY_TIME)
    def closet_preceding_finger(self, id: int) -> 'NodeInfo':
        "Return closest finger preceding this id"
        for i in range(m - 1, -1, -1):
            node = self.finger[i].node
            if node and is_alive(node) and in_interval(
                    node.id, self.id, id):
                return node
        return self.info

    # Stabilization

    def find_first_successor_alive(self) -> 'NodeInfo':
        for i in range(m):
            node = self.successor_list[i]
            if node and is_alive(node):
                return node

    @retry_if_failure(RETRY_TIME)
    def _update_successor_list(self):
        'Stabilize successor list'
        self.successor_list[0] = self.successor

        with proxy(self.successor) as remote:
            ss_list = remote.successor_list
            for i in range(1, m):
                self.successor_list[i] = ss_list[i - 1]

    @repeat(STABILIZATION_TIME * 5, lambda *args: True)
    def _stabilize_successor_list(self):
        self._update_successor_list()
        # for i in range(1,m):
        #     node = self.successor_list[i]
        #     if not node or not is_alive(node):
        #         with proxy(self.successor_list[i-1]) as remote:
        #             self.successor_list[i] = remote.successor

    @repeat(STABILIZATION_TIME, lambda *args: True)
    def _stabilize(self):
        "Periodically verify node's inmediate succesor and tell the successor about it"
        # if successor fails find first alive successor in the
        # successor list
        if not is_alive(self.successor):
            self.successor = self.find_first_successor_alive()

        try:
            with proxy(self.successor) as remote:
                node = remote.predecessor
                if node and is_alive(node) and in_interval_r(
                        node.id, self.id, self.successor.id):
                    self.successor = node
                    self._update_successor_list()
        except BaseException as why:
            print('Error in _stabilize: ' + why.__cause__)
            pass

        try:
            with proxy(self.successor) as remote:
                remote.notify(self.info)
        except Pyro4.errors.ConnectionClosedError:  # between remote._update_successor_list remote fails and this is fixed when this method is called again, so i just let ignore this exception for efficiency
            pass

    def notify(self, node: 'NodeInfo'):
        "Node think is might be our predecessor"
        if not self.predecessor or not is_alive(self.predecessor) or in_interval(
                node.id, self.predecessor.id, self.id):
            self.predecessor = node

            # Take dada from storage is needed
            for key in list(self.assured_data.keys()):
                if in_interval(key, self.predecessor.id, self.id):
                    t, value = self.assured_data.pop(key)
                    self.data[key] = value
            # Transfer data to predecessor
            transference = {}
            for key in list(self.data.keys()):
                # this interval is all the rign except this node
                # interval, is different of key < predecessor.id
                # because the rign is circular
                if in_interval(key, self.id, self.predecessor.id):
                    transference[key] = self.data.pop(key)
            # send data to predecessor node
            try:
                with proxy(self.predecessor) as remote:
                    remote.set_data(transference)
            except BaseException:
                print(
                    f'Problem sending data from {self.id} to node {self.predecessor.id}')
                # remerge data again into this node data
                self.data = {**self.data, **transference}

    @repeat(RETRY_TIME, lambda *args: True)
    def _stabilize_ensuded_data(self):
        'make a copy of it own data in the successor list store, and remove data in the node assured_data with 0 time'
        # discount time for every data in the reinsure dict and
        # delete it if time == 0
        for key in list(self.assured_data.keys()):
            _, time = self.assured_data[key]
            time -= 1
            value, _ = self.assured_data[key]
            self.assured_data[key] = value, time
            if time == 0:
                self.assured_data.pop(key)

        # send data to successor_list
        for node in list(self.successor_list):
            if not node or not is_alive(node):
                continue
            try:
                with proxy(node) as remote:
                    remote.reinsure(self.data)
            except BaseException as e:
                print(f"error transfering data for ensure: {e}")

    def reinsure(self, data: dict):
        'save and update data into the ensured data dict'
        # add new data
        for key in list(data.keys()):
            self.assured_data[key] = data[key], ASSURED_LIFE_TIME

    @repeat(STABILIZATION_TIME, lambda *args: True)
    def fix_fingers(self):
        "Periodically refresh finger table entries"
        i = random.randrange(1, m)
        self.finger[i] = self.find_successor(self.finger[i].start)

    def ping(self):
        'a simple do-nothing method for check if is this node alive in the network'
        pass

    # DATA Handling

    def set_data(self, data):
        "This is used for the successor node for transfer the correspondent data"
        self.data = {**self.data, **data}

    @retry_if_failure(RETRY_TIME)
    def save(self, key: int, value):
        node = self.find_successor(key)
        with proxy(node) as remote:
            remote.set_item(key, value)

    def set_item(self, key, value):
        print(f'set item {key}')
        self.data[key] = value

    @retry_if_failure(RETRY_TIME)
    def load(self, key):
        node = self.find_successor(key)
        with proxy(node) as remote:
            return remote.get_item(key)

    @retry_if_failure(RETRY_TIME)
    def delete(self, key):
        node = self.find_successor(key)
        with proxy(node) as remote:
            return remote.delete_item(key)

    @retry_if_failure(RETRY_TIME)
    def delete_item(self, key):
        print(f'deleting item {key}')
        try:
            self.data.pop(key)
        except:
            pass
        for node in self.successor_list:
            if node and is_alive(node):
                with proxy(node) as remote:
                    remote.unensure(key)

    def unensure(self,key):
        if key in self.assured_data:
            self.assured_data.pop(key)

    def get_item(self, key):
        return self.data[key] if self.data.__contains__(key) else None

    def print_info(self):
        info(f'Node: {self.id}')

        info(f'suc: {self.successor.id if self.successor else None}')
        info(
            f'pred: {self.predecessor.id if self.predecessor else None}')
        info(
            f's_list: {list(map(lambda node: node.id if node else None,self.successor_list))}')
        info(f'finger: {self.finger.print_fingers()}')
        info(f'keys: {list(map(lambda i:i[0],self.data.items()))}')
        info(
            f'assured: {list(map(lambda i:i[0],self.assured_data.items()))}')

    @staticmethod
    def URI(id: int, ip: str, port: int) -> str:
        return f"Pyro:{Node.Name(id)}@{ip}:{port}"

    @staticmethod
    def Name(id: int) -> str:
        return f'Node_{id}'


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
        return self.node.id if self.node else None


class FingerTable:

    def __init__(self, id):
        self.id = id
        self.fingers = []
        for i in range(m):
            start = self.fix(i)
            self.fingers.append(Finger(start, None))

    def print_fingers(self):
        return list(
            map(lambda f: f'{f.start}->{f.id}', self.fingers))

    def __getitem__(self, index: int) -> 'Finger':  # get node at this position
        return self.fingers[index]

    def __setitem__(self, index: int, node: 'NodeInfo'):  # get node at this position
        start = self.fix(index)
        self.fingers[index] = Finger(start, node)

    def fix(self, k):
        return (self.id + (1 << k)) % M


######################################################################
