import random
import Pyro4
from threading import Thread
import threading
import time
import debug.logger as log


m = 7
M = (1 << m) - 1


Pyro4.config.SERIALIZER = 'pickle'
Pyro4.config.SERIALIZERS_ACCEPTED = {
    'serpent', 'json', 'marshal', 'pickle'}

STABILIZATION_TIME = 0.2
RETRY_TIME = STABILIZATION_TIME * 4
ASSURED_LIFE_TIME = RETRY_TIME * 4


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
                    log.error(
                        f'retry {i+1}/{attempts} {func.__name__}:  {error}')
                    time.sleep(retry_delay)
                    continue
                if i > 0:
                    log.debug(f'resolve correctly function: {func.__name__} in attemt {i}')
                return result
            log.exception(f"can't handle exceptions with stabilization")
        return inner
    return decorator

# 0 entre 10 y 6


def in_interval(x: int, a: int, b: int) -> bool:
    return a < x < b if a < b else not b <= x <= a


def in_interval_r(x: int, a: int, b: int) -> bool:
    return in_interval(x, a, b) or x == b


@Pyro4.expose
class Node:
    def __init__(self, id, ip, port, chord_id: str = 'default'):
        self.id = id
        self.ip = ip
        self.port = port
        self.finger = FingerTable(self.id)
        self.data = {}
        self._successor_list = [None for _ in range(m)]
        self.assured_data = {}
        self.chord_id = chord_id

        log.init_logger(f"Node {self.id}", log.DEBUG)  # init logging
        log.debug(f"init")

    def start_serving(self, node: 'NodeInfo' = None,uri:str=None):
        '''
        node: Joint point
        '''
        log.info(f"staring serving...")
        self.pyro_daemon = Pyro4.Daemon(host=self.ip, port=self.port)
        self.pyro_daemon.register(self, self.Name(self.id))
        Thread(
            target=self.pyro_daemon.requestLoop,
            daemon=True).start()

        if not node:
            with Pyro4.Proxy(uri) as remote:
                node = remote.info
                

        if node and node.id != self.id:
            self.join(node)
        else:
            log.info('the entry id is the same, this is the initial node')
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

        log.info(f"ready and listening")

    def __del__(self):
        self.pyro_daemon.close()
        log.debug('shutdown')

    @retry_if_failure(RETRY_TIME)
    def join(self, node: 'NodeInfo'):
        "node self joins the network node is a arbitrary node in the network"
        self.predecessor = None
        with self.proxy(node) as remote:
            self.successor = remote.find_successor(self.id)
            # initialize successor_list using successor.successor_list
            log.debug(f'finded successor: {self.successor.id}')
            self._update_successor_list()
        log.debug(f"join to {node.id} succesfuly")

    @property
    def successor(self) -> 'NodeInfo':
        return self.finger[0].node

    @successor.setter
    def successor(self, value: 'NodeInfo'):
        self.finger[0] = value

    @property
    def predecessor(self) -> 'NodeInfo':
        "Node predecessor, it is a life time self.proxy"
        return self.__predecessor

    @predecessor.setter
    def predecessor(self, value: 'NodeInfo'):
        "Node predecessor, it is a life time self.proxy"
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
        with self.proxy(node) as remote:
            return remote.successor

    @retry_if_failure(RETRY_TIME)
    def find_predeccessor(self, id: int) -> 'NodeInfo':
        "Find id's precessor in Ring"
        if id == self.id:
            return self.info

        node = self.info
        node_successor = self.successor

        while not in_interval_r(id, node.id, node_successor.id):
            with self.proxy(node) as remote:
                node = remote.closet_preceding_finger(id)
            with self.proxy(node) as remote:
                node_successor = remote.successor
        return node

    @retry_if_failure(RETRY_TIME)
    def closet_preceding_finger(self, id: int) -> 'NodeInfo':
        "Return closest finger preceding this id"
        for i in range(m - 1, -1, -1):
            node = self.finger[i].node
            if node and self.is_node_alive(node) and in_interval(
                    node.id, self.id, id):
                return node
        return self.info

    # Stabilization

    def find_first_successor_alive(self) -> 'NodeInfo':
        for i in range(m):
            node = self.successor_list[i]
            if node and self.is_node_alive(node):
                return node

    @retry_if_failure(RETRY_TIME)
    def _update_successor_list(self):
        'Stabilize successor list'
        self.successor_list[0] = self.successor

        with self.proxy(self.successor) as remote:
            ss_list = remote.successor_list
            for i in range(1, m):
                self.successor_list[i] = ss_list[i - 1]

    @repeat(STABILIZATION_TIME * 5, lambda *args: True)
    def _stabilize_successor_list(self):
        self._update_successor_list()

    @repeat(STABILIZATION_TIME, lambda *args: True)
    def _stabilize(self):
        "Periodically verify node's inmediate succesor and tell the successor about it"
        # if successor fails find first alive successor in the
        # successor list
        if not self.is_node_alive(self.successor):
            self.successor = self.find_first_successor_alive()
            log.debug(f'set new succesor from successor list: {self.successor.id}')

        try:
            with self.proxy(self.successor) as remote:
                node = remote.predecessor
                if node and self.is_node_alive(node) and in_interval_r(
                        node.id, self.id, self.successor.id):
                    self.successor = node
                    log.debug(f'finded new succesor: {node.id}')
                    self._update_successor_list()
        except BaseException as why:
            pass

        try:
            with self.proxy(self.successor) as remote:
                remote.notify(self.info)
        except Pyro4.errors.ConnectionClosedError:  # between remote._update_successor_list remote fails and this is fixed when this method is called again, so i just let ignore this exception for efficiency
            pass

    def notify(self, node: 'NodeInfo'):
        "Node think is might be our predecessor"
        if not self.predecessor or not self.is_node_alive(self.predecessor) or in_interval(
                node.id, self.predecessor.id, self.id):
            self.predecessor = node
            log.debug(f'set new predecessor: {node.id}')

            # Take dada from storage is needed
            for key in list(self.assured_data.keys()):
                if in_interval(key, self.predecessor.id, self.id):
                    t, value = self.assured_data.pop(key)
                    self.data[key] = value
                    log.debug(f'assume key assured : {key}')
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
                with self.proxy(self.predecessor) as remote:
                    remote.set_data(transference)
                    log.debug(f'set data to predecessor (node {self.predecessor.id}): {list(transference.keys())}')
            except BaseException:
                log.exception(
                    f'problem sending data to node {self.predecessor.id}')
                # remerge data again into this node data
                self.data = {**self.data, **transference}

    @repeat(RETRY_TIME, lambda *args: True)
    def _stabilize_ensuded_data(self):
        'make a copy of it own data in the successor list store, and remove data in the node assured_data with 0 time'
        # discount time for every data in the reinsure dict and
        # delete it if time == 0
        for key in list(self.assured_data.keys()):
            value, time = self.assured_data[key]
            time -= 1
            self.assured_data[key] = value, time
            if time == 0:
                self.assured_data.pop(key)

        # send data to successor_list
        for node in list(self.successor_list):
            if not node or not self.is_node_alive(node):
                continue
            try:
                with self.proxy(node) as remote:
                    remote.reinsure(self.data)
            except BaseException as e:
                log.error(f"error transfering data for ensure to {node.id}")

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
        log.debug(f"call save key: {key}")
        node = self.find_successor(key)
        with self.proxy(node) as remote:
            remote.set_item(key, value)

    def set_item(self, key, value):
        log.info(f'recive key: {key}')
        self.data[key] = value

    @retry_if_failure(RETRY_TIME)
    def load(self, key):
        log.debug(f"call load key {key}")
        node = self.find_successor(key)
        with self.proxy(node) as remote:
            return remote.get_item(key)

    @retry_if_failure(RETRY_TIME)
    def delete(self, key):
        log.debug(f"call delete key {key}")
        node = self.find_successor(key)
        with self.proxy(node) as remote:
            return remote.delete_item(key)

    @retry_if_failure(RETRY_TIME)
    def delete_item(self, key):
        log.info(f'deleting key: {key}')
        try:
            self.data.pop(key)
        except BaseException:
            pass
        for node in self.successor_list:
            if node and self.is_node_alive(node):
                with self.proxy(node) as remote:
                    remote.unensure(key)

    def unensure(self, key):
        if key in self.assured_data:
            self.assured_data.pop(key)

    def get_item(self, key):
        log.info(f'returning key: {key}')
        return self.data[key] if self.data.__contains__(key) else None

    def print_info(self):
        log.debug(f'''
        suc: {self.successor.id if self.successor else None}
        pred: {self.predecessor.id if self.predecessor else None}
        s_list: {
            list(map(lambda node: node.id if node else None,self.successor_list))}
        finger: {self.finger.print_fingers()}
        keys: {list(map(lambda i:i[0],self.data.items()))}
        assured: {list(map(lambda i:i[0],self.assured_data.items()))}''')
        
    def URI(self, id: int, ip: str, port: int) -> str:
        return f"Pyro:{self.Name(id)}@{ip}:{port}"

    def Name(self, id) -> str:
        return f'chord_{self.chord_id}_node_{id}_'

    def proxy(self, node: 'NodeInfo'):
        'Pyro Proxy to that node'
        return Pyro4.Proxy(self.URI(node.id, node.ip, node.port))

    def is_node_alive(self, node: 'NodeInfo'):
        try:
            with self.proxy(node) as remote:
                remote.ping()
                return True
        except Pyro4.errors.CommunicationError:
            return False


######################################################################
class NodeInfo:
    'Represent a ChordNode information necesary to create proxies'

    def __init__(self, id: int, ip: str, port: int):
        self.id=id
        self.ip=ip
        self.port=port


class Finger:
    def __init__(self, start, node):
        self.start=start
        self.node=node

    def set(self, id, ip, port):
        self.id=id
        self.ip=ip
        self.port=port

    @property
    def id(self):
        return self.node.id if self.node else None


class FingerTable:

    def __init__(self, id):
        self.id=id
        self.fingers=[]
        for i in range(m):
            start=self.fix(i)
            self.fingers.append(Finger(start, None))

    def print_fingers(self):
        return list(
            map(lambda f: f'{f.start}->{f.id}', self.fingers))

    def __getitem__(self, index: int) -> 'Finger':  # get node at this position
        return self.fingers[index]

    def __setitem__(self, index: int, node: 'NodeInfo'):  # get node at this position
        start=self.fix(index)
        self.fingers[index]=Finger(start, node)

    def fix(self, k):
        return (self.id + (1 << k)) % M


######################################################################
