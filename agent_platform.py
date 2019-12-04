import Pyro4
from Pyro4.errors import PyroError
from utils.boostrap import Boostrap
from threading import Thread
from chord.chord import Chord
from ams import AMS

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


def initialize_servers(ip, port): # DONT USE THIS
    "Initialize the servers that will contain the platform"
    servers = [AgentPlatform(_transf_ip(ip, i), port, i) for i in range(N)]
    uris = [server.uri for server in servers]
    for server in servers:
        server.initialize_servers(uris)
    return servers


def initialize_server(ip, port):
    "Initialize one of the servers that will contain the platform"
    return AgentPlatform(ip, port, 0)


def add_server(ip, port):
    platform = get_platform(ip, port)
    ap = AgentPlatform(_transf_ip(ip, platform.get_n()), port, platform.get_n())
    platform.add_server(ap.uri)
    for k,n in platform.items():
        ap.register(k,n)
    ams = AMS(ip, port+1, platform)
    ap.register(ams.aid.name, ams.uri)
    return ap


@Pyro4.expose
class AgentPlatform:
    def __init__(self, ip, port, i):
        self.i = i
        self.n = self.i + 1
        self.ip, self.port = ip, port
        self.chord = Chord(hash(f'{ip}:{port}'), ip, port)
        self.start_serving()
        self.connections = []
        self.servers = []


    def __del__(self):
        del self.chord

    
    @property
    def get_i(self):
        return self.i

    @property
    def get_chord(self):
        return self.chord

    def start_serving(self):
        "Starts serving the platform"
        daemon = Pyro4.Daemon(self.ip, self.port)
        self.uri = daemon.register(self, f'platform_{self.i}')
        Thread(target=daemon.requestLoop).start()


    def add_server(self, uri):
        "Adds a back-up server to the platform"
        server = Pyro4.Proxy(uri)
        self.chord.join(server.get_chord)


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
        return self.chord.add(name, uri)
       

    def is_registered(self, name, uri):
        "Checks if a key is stored in the boostrap"
        return uri in self.chord.get_values()

    
    def unregister(self, name):
        "Unregisters a key in the boostrap"
        print('--------------------------------')
        print(f'Eliminando id: {name}')
        self.chord.delete_key(name)

    
    def get_node(self):
        "Gets a random node from the boostrap"
        return self.chord.get_value()
