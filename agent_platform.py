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
    n = 0 if n == 255 else n + i
    strings[-1] = str(n)
    return '.'.join(strings)
    

def build_uri(id_, ip, port):
    "Builds an uri given the value of the identifier, ip and a port"
    return 'PYRO:{}@{}:{}'.format(id_, ip, port)


def get_platform(ip, port):
    "Gets the first functional platform given by a port"
    for i in range(N):
        platform_uri = build_uri(f'platform_{i}', _transf_ip(ip, i), port+i)
        try:
            platform = Pyro4.Proxy(platform_uri)
            platform.ping()
            return platform
        except PyroError:
            continue
    raise Exception("No se pudo encontrar una plataforma disponible")


def get_identificator(ip, port):
    "Gets the first valid id for the platform"
    for i in range(N):
        platform_uri = build_uri(f'platform_{i}', _transf_ip(ip, i), port+i)
        try:
            with Pyro4.Proxy(platform_uri) as platform:
                platform.ping()
        except PyroError:
            return i
    raise Exception('Ya no se pueden añadir más servidores a la plataforma')



def initialize_server(ip, port):
    "Initialize one of the servers that will contain the platform"
    ap = AgentPlatform(ip, port, 0, 'platform_' + f'{ip}:{port}')
    ap.join()
    return ap


def add_server(ip, port):
    platform = get_platform(ip, port)
    id_ = get_identificator(ip, port)
    new_ip = _transf_ip(ip, id_)
    ap = AgentPlatform(new_ip, port+id_, id_, 'platform_' + f'{ip}:{port}')
    platform.add_server(ap.uri)
    ams = AMS(ip, randint(1024, 10000), 'ams_' + f'{ip}:{port}')
    ap.register(ams.aid.name, ams.uri)
    return ap


@Pyro4.expose
class AgentPlatform:
    def __init__(self, ip, port, i, chord_id):
        self.i = i
        self.ip, self.port = ip, port
        hash_ = get_hash(f'{ip}:{port}')
        self.chord = Chord(hash_, ip, randint(1024, 10000), chord_id)
        self.start_serving()
        self.connections = []
        self.servers = []
        self.ams_chord_id = None


    def __del__(self):
        del self.chord

    def join(self, uri=None):
        self.chord.join(uri)


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
            ams_chord_id = None
        with Pyro4.Proxy(uri) as ams:
            ams.join(ams_chord_id)
        name_id = get_hash(name)
        self.chord.storage(name_id, uri)
       

    def is_registered(self, name, uri):
        "Checks if a key is stored in the boostrap"     
        name_id = get_hash(name)
        if not name_id:
            return False
        uri_stored = self.chord.get(name_id)
        return uri_stored == uri

    
    def unregister(self, name):
        "Unregisters a key in the boostrap"
        print('--------------------------------')
        print(f'Eliminando id: {name}')
        self.chord.remove(get_hash(name))

    
    def get_item(self, name):
        name_id = get_hash(name)
        return self.chord.get(name_id)

    def get_node(self):
        "Gets a random node from the boostrap"
        key = self.chord.get_first_key()
        if not key:
            raise Exception('No existe ningún elemento.')
        uri = self.chord.get(key)
        try:
            with Pyro4.Proxy(uri) as ams:
                ams.ping()
            return uri
        except:
            self.chord.remove(key)
            return self.get_node()
