import Pyro4
from Pyro4.errors import PyroError
from utils.boostrap import Boostrap
from threading import Thread
from chord.chord import Chord
from ams import AMS
import hashlib
from chord.node import get_hash
from random import randint

N = 5


def _transf_ip(ip, i):
    strings = ip.split('.')
    n = int(strings[-1])
    n = 255 if n == 0 else n - i
    strings[-1] = str(n)
    return '.'.join(strings)
    

def build_uri(id_, ip, port):
    "Builds an uri given the value of the identifier, ip and a port"
    return 'PYRO:{}@{}:{}'.format(id_, ip, port)


def get_platform(ip, port):
    "Gets the first functional platform given by a port"
    for i in range(N):
        platform_uri = build_uri(f'platform_{i}', _transf_ip(ip, i), port)
        try:
            platform = Pyro4.Proxy(platform_uri)
            platform.ping()
            return platform
        except PyroError:
            continue
    raise Exception("No se pudo encontrar una plataforma disponible")


def initialize_server(ip, port):
    "Initialize one of the servers that will contain the platform"
    ap = AgentPlatform(ip, port, 0)
    ap.join()
    return ap

def add_server(ip, port):
    platform = get_platform(ip, port)
    ip = _transf_ip(ip, platform.n)
    ap = AgentPlatform(ip, port+platform.i, platform.n)
    platform.add_server(ap.uri)
    ams = AMS(ip, randint(1024, 10000))
    ap.register(ams.aid.name, ams.uri)
    return ap


@Pyro4.expose
class AgentPlatform:
    def __init__(self, ip, port, i):
        self._i = i
        self._n = self._i + 1
        self.ip, self.port = ip, port
        self.start_serving()
        hash_ = get_hash(f'{ip}:{port}')
        self.chord = Chord(hash_, ip, port + 1, 'platform')
        self.connections = []
        self.servers = []
        self.ams_chord_id = None


    def __del__(self):
        del self.chord

    def join(self, uri=None):
        self.chord.join(uri)

    @property
    def i(self):
        return self._i

    @property
    def n(self):
        return self._n

    @property
    def chord_id(self):
        return self.chord.get_id()

    def get_ams_chord_id(self):
        ams_uri = self.get_node()
        with Pyro4.Proxy(ams_uri) as ams:
            return ams.get_chord_id()


    def start_serving(self):
        "Starts serving the platform"
        daemon = Pyro4.Daemon(self.ip, self.port)
        self.uri = daemon.register(self, f'platform_{self.i}')
        Thread(target=daemon.requestLoop, daemon=True).start()


    def add_server(self, uri):
        "Adds a back-up server to the platform"
        print('--------------------------------')
        print(f'Adding server: {uri} to the platform')
        with Pyro4.Proxy(uri) as server:
            server.join(self.chord_id)

    def ping(self):
        "Checks if the platform is alive"
        return True


    def register(self, name, uri):
        """
        Registers a key in the bootstrap of the platform and replicates 
        this entry in all the other servers
        """
        print('--------------------------------')
        print(f'Registering id: {name} with value: {uri}')
        try:
            ams_chord_id = self.get_ams_chord_id()            
        except:
            print('Problem')
            ams_chord_id = None
        with Pyro4.Proxy(uri) as ams:
            ams.join(ams_chord_id)
        name_id = get_hash(name)
        self.chord.storage(name_id, uri)
       

    def is_registered(self, name, uri):
        "Checks if a key is stored in the boostrap"
        #? que pasa si no se encuentra una llave        
        name_id = get_hash(name)
        if not name_id:
            return False
        uri_stored = self.chord.get(name_id)
        return uri_stored == uri

    
    def unregister(self, name):
        "Unregisters a key in the boostrap"
        print('--------------------------------')
        print(f'Eliminando id: {name}')
        self.chord.remove(name)

    
    def get_item(self, name):
        name_id = get_hash(name)
        return self.chord.get(name_id)

    def get_node(self):
        "Gets a random node from the boostrap"
        return self.chord.get_first()
