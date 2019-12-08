from agent import BaseAgent
from utils.aid import AID
from utils.agent_descriptions import AMSAgentDescription
from threading import Thread
from chord.chord import Chord
import Pyro4, json
import json
from random import random
from utils.broadcast import broadcast_server, broadcast_client


def build_uri(id_, ip, port):
    "Builds an uri given the value of the identifier, ip and a port"
    return 'PYRO:{}@{}:{}'.format(id_, ip, port)

def get_ams_fixed_uri(ip, port):
    return build_uri('ams', ip, port)

def get_ams(id_):
    ams_uri = get_ams_uri(id_)
    return Pyro4.Proxy(ams_uri)

def get_ams_uri(id_):
    "Gets the first functional ams given by an id"
    try:
        address = broadcast_client(7371, id_)
        ip, port = address.split(':')
        port = int(port)
        return build_uri(f'ams', ip, port)
    except:
        raise Exception("No se pudo encontrar una plataforma disponible")
 
def get_ams_id(id_):
    "Gets the ams id to join a new ams"
    try:
        address = broadcast_client(7371, id_)
        ip, port = address.split(':')
        port = int(port)
        ams_uri = get_ams_uri(id_)
        with Pyro4.Proxy(ams_uri) as ams:
            return ams.get_id()
    except:
        raise Exception('No se pudo encontrar una plataforma disponible')

@Pyro4.expose
class AMS(BaseAgent):
    def __init__(self, host, port, chord_id):
        self.aid = AID(f'ams@{host}:{port}')
        self.host = host
        self.port = port
        self.address = f'{self.host}:{self.port}'
        self.agents = [] # estructura que guardará los agentes en la plataforma
        self.id = chord_id
        self.start_serving()
        self.chord = Chord(hash(self.aid), self.host, self.port+1, chord_id)


    def __del__(self):
        del self.chord
        
    def join(self, uri=None):
        self.chord.join(uri)

    def get_id(self):
        return self.chord.get_id()

    def start_serving(self):
        print('---------------------------------')
        localname = self.aid.localname
        print(f'Sirviendo el agente {localname}')
        try:
            daemon = Pyro4.Daemon(self.aid.host, self.aid.port)
            self.uri = daemon.register(self, localname)
            print(f'La uri de {self.aid.name} es {self.uri}')
            Thread(target=daemon.requestLoop, daemon=True).start()
            Thread(target=broadcast_server, args=(7371, self.id, self.address), daemon=True).start()            
            return True
        except Exception as e:
            print(f'Error al arrancar el agente {localname}')
            print(f'Text error: {e}')
            return False


    def get_chord_id(self):
        return self.chord.get_id()

    def load_json(self, obj):
        return json.loads(obj)


    def search_service(self, name):
        return self.chord.get_all(lambda x: name in self.load_json(x)['services'])


    def search_agent_by_service(self, name):
        return self.chord.get_first(lambda x: name in self.load_json(x)['services'])


    def register(self, agent_name, uri, services, state=0):
        "Registers an agent into the ams"
        aid = AID(agent_name, resolvers=[self.aid])
        ams_desc = AMSAgentDescription(aid, state, services, uri.asString())
        self.chord.storage(hash(aid), ams_desc.dumps())
        

    def ping(self):
        "Checks if the ams is alive"
        return True

    def deregister(self, aid):
        "Deregisters an agent in the ams"
        self.chord.remove(hash(aid))

    
    def get_agents(self):
        "Returns all the agens in the platform"
        return self.chord.get_all()
        

    def get_local_agents(self):
        "Returns all the agents of the ams"
        return self.chord.get_locals()

    
    def search(self, aid):
        "Searchs for the description of an agent in the ams"
        try:
            desc = self.chord.get(hash(aid))
            return AMSAgentDescription.loads(desc)
        except:
            raise Exception(f'No se puede encontrar al agente {aid.name}')


    def stop_agent(self, aid):
        "Stops an agent"
        agent = self.get_agent_proxy(aid)
        if agent is None:
            return
        try:
            agent.stop()
        except:
            raise Exception(f'No se puede contactar con el agent {aid.name}')
    
    def restart_agent(self, aid):
        "Resumes the execution of an agent"
        agent = self.get_agent_proxy(aid)
        if agent is None:
            return
        try:
            agent.restart()
        except:
            raise Exception(f'No se puede contactar con el agent {aid.name}')

    
    def end_agent(self, aid):
        "Ends the execution of an agent"
        agent = self.get_agent_proxy(aid)
        if agent is None:
            return
        try:
            agent.end()
        except:
            raise Exception(f'No se puede contactar con el agente {aid.name}')
    
    def get_agent_status(self, aid):
        "Gets the state of an agent"
        agent = self.get_agent_proxy(aid)
        if agent is None:
            return
        try:
            return agent.get_status()
        except:
            raise Exception(f'No se puede contactar con el agente {aid.name}')

    def get_agent_proxy(self, aid):
        print(f'Buscando el agente: {aid.name}')
        agent_desc = self.search(aid)
        print(f'Agente encontrado en el AMS, contactando con el agente...')
        try:
            agent = Pyro4.Proxy(agent_desc.uri)
            agent.ping()
        except:
            Exception(f'No se puede contactar con el agente {aid.name}')
        return agent


    def execute_agent(self, aid, methods):
        "Excecutes the agent with the requiered aid"
        print('---------------------------------------')
        print(f'Solicitando la ejecución del cliente: {aid.name}')
        agent = self.get_agent_proxy(aid)
        if agent is None:
            print(f'No se puede encontrar al agente {aid.name} en la plataforma')
            return
        print('Contactado exitosamente')
        for meth in methods:
            self._execute_meth(agent, meth)


    def _execute_meth(self, agent_proxy, method, *args):
        if agent_proxy is None:
            print(f'No se pudo encontrar al agente en la plataforma')
            return
        print(f'Ejecutando el método: {method}')
        try:
            return agent_proxy.run_behaviour(method, *args)
        except:
            raise Exception(f'No se pudo contactar con el agente')

    def execute_method(self, aid, method, *args):
        "Executes the agent the agent with the required aid"
        print('---------------------------------------')
        print(f'Solicitando la ejecución del cliente: {aid.name}')
        agent = self.get_agent_proxy(aid)
        return self._execute_meth(agent, method, *args)
