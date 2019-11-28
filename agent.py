from utils.aid import AID
import Pyro4
from threading import Thread

# Agents states
INITIATED = 0   # The Agent object is built, but hasn't registered itself yet with the AMS, has neither a name nor an address and cannot communicate with other agents.
ACTIVE = 1      # The Agent object is registered with the AMS, has a regular name and address and can access all the various JADE features.
BUSY = 2        # The Agent object is currently bussy. Some agent behaviour is being executed
WAITING = 3     # The Agent object is blocked, waiting for something. Its internal thread is sleeping and will wake up when some condition is met (typically when a  message arrives).
DELETED = 4     # The Agent is definitely dead. The internal thread has terminated its execution and the Agent is no more registered with the AMS. 

@Pyro4.expose
class BaseAgent:
    def __init__(self, aid):
        self.aid = aid
        self.behaviours = {}
        self.name = aid.localname
        self.state = INITIATED
        self.setup()
        self.start_serving()
        self.active_threads = []

    def start_serving(self):
        print('---------------------------------')
        localname = self.aid.localname
        print(f'Sirviendo el agente {localname}')
        try:
            daemon = Pyro4.Daemon(self.aid.host, self.aid.port)
            self.uri = daemon.register(self)
            print(f'La uri de {self.aid.name} es {self.uri}')
            Thread(target=daemon.requestLoop).start()
            return True
        except Exception as e:
            print(f'Error al arrancar el agente {localname}')
            print(f'Text error: {e}')
            return False

    def setup(self):
        "Setups agent method"
        pass

    def receive(self):
        """Returns the first message of the message queue (removing it)
        or None if the message queue is empty"""
        pass

    def send(self, message):
        """Sends an ACL message to the agents specified
        in the receivers parameter of the ACL message.
        """
        pass

    def suspend(self):
        "Suspends the agent"
        self.state = SUSPENDED

    def end(self):
        "Ends the execution of an agent"
        self.state = ACTIVE
        self.remove_inactive_behaviours()
        # TODO: Buscar una manera de parar un hilo
        # for t in self.active_threads:
        #     print('Here')
        #     t._stop()

    def run_behaviour(self, name, *args):
        try:
            b = self.behaviours[name]
            # TODO: buscar como coger el resultado de un hilo
            t = Thread(target=self.execute_behaviour, args=(b, name, *args))
            self.active_threads.append(t)
            t.start()
        except KeyError:
            print(f'El servicio solicitado: {name} no existe')
    
    def remove_inactive_behaviours(self):
        "Checks all the behaviours that don't execute"
        threads = [t for t in self.active_threads]
        for t in threads:
            if not t.is_alive():
                self.active_threads.remove(t)

    def execute_behaviour(self, behaviour, name, *args):
        b = behaviour(name) 
        return b.run(*args)

    def add_behaviour(self, name, b):
        self.behaviours[name] = b

@Pyro4.expose
class Agent(BaseAgent):
    # def __init__(self, aid):
        # super().__init__(AID(name, addresses, resolvers))
        
    def register_ams(self, ams_uri):
        "Registers the agent in a given ams"
        try:
            ams = Pyro4.Proxy(ams_uri)
            ams.register(self.aid.name, self.uri)
        except Exception as e:
            print(e)

    # def register_ams(self, ams):
    #     ams.register(self.aid.name, self.name)

    def register_df(self, df):
        "Registers the agent in a given df"
        pass


if __name__ == "__main__":
    pass