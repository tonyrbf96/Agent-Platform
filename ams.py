from agent import BaseAgent
from utils.aid import AID
from utils.agent_descriptions import AMSAgentDescription
from mts import MTS
import Pyro4

class AMS(BaseAgent):
    def __init__(self, host, port):
        self.aid = AID(f'ams@{host}:{port}')
        self.host = host
        self.port = port
        self.agents = {} # estructura que guardará los agentes en la plataforma
        self.mts = MTS()

    def register(self, agent, state=0):
        "Registers an agent in the ams"
        self.agents[1] = AMSAgentDescription(agent.aid, state, agent.uri)

    def deregister(self, aid):
        "Deregisters an agent in the ams"
        pass

    def modify(self, aid, state):
        "Modifies the state of an agent"
        pass

    def search(self, aid):
        "Searchs for the description of an agent in the ams"
        for ad in self.agents.values():
            if ad.aid.name == aid.name:
                return ad
        raise Exception('Cannot find the agent')
        

    def suspend_agent(self, aid):
        "Suspends an agent"
        pass

    def resume_agent(self, aid):
        "Resumes the execution of an agent"
        pass

    def end_agent(self, aid):
        "Finishes the execution of an agent"
        pass

    def execute_agent(self, aid, methods):
        "Excecutes the agent with the requiered aid"
        print('---------------------------------------')
        print(f'Solicitando la ejecución del cliente: {aid.localname}')
        agent_desc = self.search(aid)
        print('Agente encontrado en el AMS, contactando con el cliente...')
        agent = Pyro4.Proxy(agent_desc.uri)
        print('Contactado exitosamente')
        for meth in methods:
            print(f'Ejecutando el método: {meth}')
            agent.run_behaviour(meth)
        print('Terminando')