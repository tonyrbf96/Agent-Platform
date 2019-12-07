from utils.aid import AID
import Pyro4
from threading import Thread

# Agents states
INITIATED = 0   # The Agent object is built, but hasn't registered itself yet with the AMS, has neither a name nor an address and cannot communicate with other agents.
ACTIVE    = 1   # The Agent object is registered with the AMS, has a regular name and address and can access all the various features.
BUSY      = 2   # The Agent object is currently bussy. Some agent behaviour is being executed
STOPPED   = 3   # The Agent object is blocked, waiting for something. 
DELETED   = 4   # The Agent is definitely dead. The internal thread has terminated its execution

@Pyro4.expose
class BaseAgent:
    def __init__(self, aid):
        self.aid = aid
        self.behaviours = {}
        self.name = aid.name
        self.state = INITIATED
        self.setup()
        res = self.start_serving()
        if not res:
            raise Exception('Error al iniciar el agente')
        self.active_behaviours = []
        self.stopped_behaviours = []
        self.state = INITIATED

    def ping(self):
        return True
   
    def start_serving(self):
        print('---------------------------------')
        localname = self.aid.localname
        print(f'Sirviendo el agente {localname}')
        try:
            daemon = Pyro4.Daemon(self.aid.host, self.aid.port)
            self.uri = daemon.register(self, localname)
            print(f'La uri de {self.aid.name} es {self.uri}')
            Thread(target=daemon.requestLoop, daemon=True).start()
            return True
        except Exception as e:
            print(f'Error al arrancar el agente {localname}')
            print(f'Text error: {e}')
            return False

   
    def setup(self):
        "Setups agent method"
        pass

   
    def end(self):
        "Ends the execution of an agent"
        self.state = ACTIVE
        for b in self.active_behaviours:
            b.end()
        self.active_behaviours = []


    def stop(self):
        "Stops the execution of an agent"
        for b in self.active_behaviours:
            b.stop()
            self.stopped_behaviours.append(b)
        if self.stopped_behaviours:
            self.state = STOPPED


    def restart(self):
        "Restarts the execution of an agent"
        for b in self.stopped_behaviours:
            b.restart()
        if self.stopped_behaviours:
            self.state = BUSY
        self.stopped_behaviours = []

    
    def get_status(self):
        return self.state


    def run_behaviour(self, name, *args):
        try:
            b = self.behaviours[name]
            Thread(target=self.execute_behaviour, args=(b, name, *args), daemon=True).start()
            self.state = BUSY
        except KeyError:
            print(f'El servicio solicitado: {name} no existe')
        except:
            print(f'Error ejecutando la función {name} con los parámetros {args}')

   
    def execute_behaviour(self, behaviour, name, *args):
        try:
            b = behaviour(name) 
            self.active_behaviours.append(b)
            b.on_start(*args)
            return b.run(*args)
        except TypeError as e:
            print(e)

   
    def add_behaviour(self, name, b):
        self.behaviours[name] = b


@Pyro4.expose
class Agent(BaseAgent):
    def register_ams(self, ams_uri):
        self.state = ACTIVE
        "Registers the agent in a given ams"
        try:
            with Pyro4.Proxy(ams_uri) as ams:
                ams.register(self.aid.name, self.uri, list(self.behaviours.keys()))
        except Exception as e:
            print(e)

    def register_df(self, df):
        "Registers the agent in a given df"
        pass


if __name__ == "__main__":
    pass