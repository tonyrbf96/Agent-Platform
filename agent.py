from utils.aid import AID
import Pyro4
from threading import Thread

# Agents states
INITIATED = 0   # The Agent object is built, but hasn't registered itself yet with the AMS, has neither a name nor an address and cannot communicate with other agents.
ACTIVE = 1      # The Agent object is registered with the AMS, has a regular name and address and can access all the various JADE features.
SUSPENDED = 2   # The Agent object is currently stopped. Its internal thread is suspended and no agent behaviour is being executed
WAITING = 3     # The Agent object is blocked, waiting for something. Its internal thread is sleeping and will wake up when some condition is met (typically when a  message arrives).
DELETED = 4     # The Agent is definitely dead. The internal thread has terminated its execution and the Agent is no more registered with the AMS. 

@Pyro4.expose
class BaseAgent:
    def __init__(self, mts, aid):
        self.aid = aid
        self.behaviours = {}
        self.mts = mts
        self.name = aid.localname
        self.state = INITIATED
        self.setup()
        self.start_serving()

    def start_serving(self):
        print('---------------------------------')
        localname = self.aid.localname
        print(f'Sirviendo el agente {localname}')
        try:
            daemon = Pyro4.Daemon(self.aid.host, self.aid.port)
            self.uri = daemon.register(self)
            Thread(target=daemon.requestLoop).start()
            return True
        except Exception:
            print(f'Error al arrancar el agente {localname}')
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

    def run_behaviour(self, name):
        try:
            b = self.behaviours[name]
            b.on_start()
            b.run()
            b.on_end()
        except KeyError:
            raise Exception(f'El servicio solicitado: {name} no existe')
    
    def add_behaviour(self, b):
        self.behaviours[b.name] = b



class Agent(BaseAgent):
    def __init__(self, mts, name:str, addresses:list=None, resolvers:list=None):
        super().__init__(mts, AID(name, addresses, resolvers))
        
    def register_ams(self, ams):
        "Registers the agent in a given ams"
        self.ams = ams
        ams.register(self)

    def register_df(self, df):
        "Registers the agent in a given df"
        pass


if __name__ == "__main__":
    pass