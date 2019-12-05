import Pyro4
from Pyro4.errors import PyroError
from utils.boostrap import Boostrap
from threading import Thread
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
    ap = AgentPlatform(ip, port, 0)
    ap.connections.append(ap)
    ap.servers.append(ap.uri)
    return ap

def add_server(ip, port):
    platform = get_platform(ip, port)
    ap = AgentPlatform(_transf_ip(ip, platform.get_n()), port, platform.get_n())
    platform.add_server(ap.uri)
    for k,n in platform.items():
        ap.add_boostrap(k,n)
    ams = AMS(ip, port+1, platform)
    ap.register(ams.aid.name, ams.uri)
    return ap

@Pyro4.expose
class AgentPlatform:
    def __init__(self, ip, port, i):
        self.i = i
        self.n = self.i + 1
        self.ip, self.port = ip, port
        self.boostrap = Boostrap()
        self.start_serving()
        self.connections = []
        self.servers = []


    def __del__(self):
        print('Hello desde la plataforma')

    def __getitem__(self, value):
        return self.boostrap.table[value]

    def items(self):
        for k, v in self.boostrap:
            yield k, v
    
    @property
    def get_i(self):
        return self.i

    def get_n(self):
        return self.n

    def get_item(self, value):
        return self[value]

    def add_boostrap(self, name, uri):
        return self.boostrap.register(name, uri)

    def remove_boostrap(self, name):
        self.boostrap.unregister(name)

    def start_serving(self):
        "Starts serving the platform"
        daemon = Pyro4.Daemon(self.ip, self.port)
        self.uri = daemon.register(self, f'platform_{self.i}')
        print(self.uri)
        Thread(target=daemon.requestLoop, daemon=True).start()


    def initialize_servers(self, servers_uri): # DONT USE THIS
        "Initialize all the copies servers of the platform"
        self.servers = servers_uri
        for i, uri in enumerate(servers_uri):
            if self.uri == uri:
                self.i = i
                self.connections.append(self)
            else:
                self.connections.append(Pyro4.Proxy(uri))        
        self.up = self.connections


    def add_server(self, server_uri):
        "Adds a back-up server to the platform"
        self.connections.append(Pyro4.Proxy(server_uri))
        self.servers.append(server_uri)
        self.n += 1
        # changing the connections and the servers list of all previous servers
        for i, c in enumerate(self.connections):
            if i != self.i: 
                try: 
                    c.add_connections(self.connections, self.servers)
                except PyroError:
                    pass
                c.change_connections(c.get_i, c)


    def change_connections(self, i, value):
        self.connections[i] = value

    def add_connections(self, connections, servers):
        self.connections = [c for c in connections]
        self.servers = [s for s in servers]
        self.n = len(connections)



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
                server.add_boostrap(name, uri)
            except PyroError:
                print(f"Se ha caido el servidor {server.i}")
        # return self.add_boostrap(name, uri)


    def is_registered(self, name, uri):
        "Checks if a key is stored in the boostrap"
        return self.boostrap.is_registered(name, uri)

    
    def unregister(self, name):
        "Unregisters a key in the boostrap"
        print('--------------------------------')
        print(f'Eliminando id: {name}')
        for server in self.connections:
            try:
                server.remove_boostrap(name)
            except PyroError:
                print(f"Se ha caido el servidor {server.i}")
        # self.remove_boostrap(name)

    
    def get_node(self):
        "Gets a random node from the boostrap"
        return self.boostrap.get_node()
