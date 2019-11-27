from agent import BaseAgent
from utils.aid import AID
from utils.agent_descriptions import AMSAgentDescription
from threading import Thread
from chord.chord import Chord
import Pyro4, json

@Pyro4.expose
class AMS(BaseAgent):
    def __init__(self, host, port):
        self.aid = AID(f'ams@{host}:{port}')
        self.host = host
        self.port = port
        self.agents = {} # estructura que guardará los agentes en la plataforma
        self.chord = Chord(hash(self.aid))
        self.start_serving()
        # se añade el ams al anillo de chord


    def register(self, aid, uri, state=0):
        "Registers an agent in the ams"
        ams_desc = AMSAgentDescription(aid, state, uri)
        self.agents[len(self.agents)] = ams_desc
        # #? Not sure if i can save the object in the node through pyro
        # self.chord.add(hash(aid), ams_desc.dumps())
        

    def deregister(self, aid):
        "Deregisters an agent in the ams"
        self.chord.delete_key(hash(aid))


    def modify(self, aid, state):
        "Modifies the state of an agent"
        # not important...
        pass


    def search(self, aid):
        "Searchs for the description of an agent in the ams"
        for ad in self.agents.values():
            if ad.aid == aid:
                return ad
        raise Exception(f'Cannot find the agent {aid}')
        # try:
        #     json_desc = self.chord.get(hash(aid))
        #     return AMSAgentDescription.loads(json_desc)
        # except:
        #     raise Exception(f'Cannot find the agent {aid}')


    def suspend_agent(self, aid):
        "Suspends an agent"
        pass


    def resume_agent(self, aid):
        "Resumes the execution of an agent"
        pass


    def end_agent(self, aid):
        "Finishes the execution of an agent"
        agent = self.get_agent_proxy(aid)
        if agent == None:
            return
        agent.end()
        print('Execution of the agent ended')
    

    def get_agent_proxy(self, aid):
        try: 
            print(f'Buscando el agente: {aid}')
            agent_desc = self.search(aid)
            print(f'Agente encontrado en el AMS, contactando con el cliente...')
            return Pyro4.Proxy(agent_desc.uri)
        except Exception as e:
            print(e)
        return None


    def execute_agent(self, aid, methods):
        "Excecutes the agent with the requiered aid"
        print('---------------------------------------')
        print(f'Solicitando la ejecución del cliente: {aid}')
        agent = self.get_agent_proxy(aid)
        if agent is None:
            print(f'No se pudo encontrar el agent {aid} en la plataforma')
            return
        print('Contactado exitosamente')
        for meth in methods:
            self._execute_meth(agent, meth)


    def _execute_meth(self, agent_proxy, method, *args):
        if agent_proxy is None:
            print(f'No se pudo encontrar al agente en la plataforma')
            return
        print(f'Ejecutando el método: {method}')
        return agent_proxy.run_behaviour(method, *args)


    def execute_method(self, aid, method, *args):
        "Executes the agent the agent with the required aid"
        print('---------------------------------------')
        print(f'Solicitando la ejecución del cliente: {aid}')
        agent = self.get_agent_proxy(aid)
        return self._execute_meth(agent, method, *args)
