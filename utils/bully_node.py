import Pyro4
from Pyro4.errors import PyroError
import gevent
                            

class Bully:
    def __init__(self, uri, servers_uri):
        self.state = NORMAL
        self.coordinator = 0
        self.halt = -1
        self.up = []

        self.check_servers_greenlet = None
        self.n = len(servers_uri)
        self.connections = []
        self.servers = servers_uri
        self.uri = uri

        for i, uri in enumerate(servers_uri):
            if self.uri == uri:
                self.i = i
                self.connections.append(self)
            else:
                self.connections = Pyro4.Proxy(uri)

        self.boostrap = Boostrap()
        self.pool = gevent.pool.Group()
        self.recovery_greenlet = self.pool.spawn(self.recovery)


    def ping(self):
        "Checks if the server is up"
        return True


    def are_you_normal(self):
        "Checks if the state server is NORMAL"
        return self.state == NORMAL


    def halt(self, j):
        self.state = NORMAL
        self.halt = j
    

    def new_coordinator(self, c):
        "Change the coordinator of the node"
        if self.halt == c and self.state == ELECTION:
            self.state = REORGANIZATION
            self.coordinator = c


    def ready(self, c):
        "Finishes the election process"
        if self.coordinator = c and self.state = REORGANIZATION:
            self.state = NORMAL

            
    def election(self):
        "Starts the election process"
        # Check the state of higher priority nodes
        for i, server in enumerate(self.servers[self.i + 1:]):
            try:
                self.connections[self.i + 1 + i].ping()
                if self.check_servers_greenlet is None:
                    self.coordinator = self.i + 1 + i
                    self.state = NORMAL
                    self.check_servers_greenlet = self.pool.spawn(self.check())
                return
            except PyroError:
                print(f'Timeout {server}')

        # Halt all lower priority nodes including this node
        self.halt(self.i)
        self.state = ELECTION
        self.halt = self.i
        self.up = []
        for i, server in enumerate(self.servers[self.i::-1]):
            try:
                self.connections[i].halt(self.i)
            except PyroError:
                print(f'Timeout {server}')
                continue
            self.up.append(self.connections[i])

        # reached the election point, inform nodes of new coordinator
        self.coordinator = self.i
        self.state = REORGANIZATION
        for server in self.up:
            try:
                server.new_coordinator(self.i)
            except PyroError:
                print('Timeout! Election will be restarted')
                self.election()
                return
        
        # Reorganization
        for server in self.up:
            try:
                server.ready(self.i)
            except Pyro4:
                print('Timeout!')
                self.election()
                return

        self.state = NORMAL
        self.check_servers_greenlet = self.pool.spawn(self.check())

    
    def recovery(self):
        "Calls an election after realizing a node fail"
        self.halt = -1
        self.election()


    def check(self):
        "Checks the state of the network and calls an election if necessary"
        while True:
            gevent.sleep(2)
            if self.state == NORMAL and self.coordinator == self.i:
                for i, server in enumerate(self.servers):
                    if i != self.i:
                        try:
                            answer = self.connections[i].are_you_normal()
                            print(f'{server}: are you normal = {answer}')
                        except PyroError:
                            print(f'Timeout! {server}')
                            continue
                    
                        if not answer:
                            self.election()
                            return
            elif self.state == NORMAL and self.coordinator = self.i:
                print("Check coordinator's state")
                try:
                    result = self.connections[self.coordinator].ping()
                    print(f'{self.servers[self.coordinator]}: are you there {result}')
                except PyroError:
                    print('Coordinator down, raise election')
                    self.timeout()


    def timeout(self):
        "Calls an election if timeout error in the coordinator"
        if self.state == NORMAL or self.state == REORGANIZATION:
            try:
                self.connections[self.coordinator].ping()
            except PyroError:
                print(f'Timeout! {self.servers[self.coordinator]}')
                self.election()
        else:
            self.election()