import Pyro4
from Pyro4.errors import PyroErrors
from utils.boostrap import Boostrap
from threading import Thread
import gevent


N = 5

#TODO: Estoy operando con los ip y tengo q coger el # después del último .


def build_uri(id_, ip, port):
    "Builds an uri given the value of the identifier, ip and a port"
    id_ = id_.replace('@', 'at')
    return 'PYRO:{}@{}:{}'.format(id_, ip, port)


def get_platform(ip, port):
    "Gets the first functional platform given by a port"
    for i in range(N):
        platform_uri = build_uri(f'platform_{i}', ip-i, port)
        try:
            platform = Pyro4.Proxy(platform_uri)
            platform.ping()
            return platform
        except PyroErrors:
            continue
    raise Exception("No se pudo encontrar una plataforma disponible")


def initialize_servers(ip, port):
    "Initialize the servers that will contain the platform"
    servers = [AgentPlatform(ip-i, port, N, i) for i in range(N)]
    uris = [server.uri for server in servers]
    for server, uri in zip(servers, uris):
        server.initialize_serves(uri, uris)
    return servers


@Pyro4.expose
class AgentPlatform:
    def __init__(self, ip, port, i):
        self.i = i
        self.n = N
        self.ip, self.port = ip, port
        self.boostrap = Boostrap()
        self.start_serving()


    def __getitem__(self, value):
        return self.boostrap.table[value]


    def start_serving(self):
        "Starts serving the platform"
        daemon = Pyro4.Daemon(self.ip, self.port)
        self.uri = daemon.register(self, f'plarform_{self.i}')
        Thread(target=daemon.requestLoop).start()


    def initialize_servers(self, uri, servers_uri):
        "Initialize all the copies servers of the platform"
        self.connections = []
        self.servers = servers_uri
        self.uri = uri
        for i, uri in enumerate(servers_uri):
            if self.uri == uri:
                self.i = i
                self.connections.append(self)
            else:
                self.connections = Pyro4.Proxy(uri)        
        self.up = self.connections


    def ping(self):
        "Checks if the platform is alive"
        return True


    def register(self, name, uri):
        """
        Registers a key in the bootstrap of the platform and replicates 
        this entry in all the other servers
        """
        for server in self.connections:
            try:
                server.boostrap.register(name, uri)
            except PyroErrors:
                print(f"Se ha caido el servidor {server.i}")
        return self.boostrap.register(name, uri)


    def is_registered(self, name, uri):
        "Checks if a key is stored in the boostrap"
        return self.boostrap.is_registerd(name, uri)

    
    def unregister(self, name):
        "Unregisters a key in the boostrap"
        print('--------------------------------')
        print(f'Eliminando id: {name}')
        for server in self.connections:
            try:
                server.boostrap.unregister(name)
            except PyroErrors:
                print(f"Se ha caido el servidor {server.i}")
        self.boostrap.unregister(name)

    
    def get_node(self):
        "Gets a random node from the boostrap"
        return self.boostrap.get_node()
