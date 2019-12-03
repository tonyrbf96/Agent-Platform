from agent import BaseAgent
from utils.aid import AID
from utils.agent_descriptions import AMSAgentDescription
from threading import Thread
from chord.chord import Chord
import Pyro4, json

@Pyro4.expose
class AMS(BaseAgent):
    def __init__(self, host, port, platform):
        self.aid = AID(f'ams@{host}:{port}')
        self.host = host
        self.port = port
        self.agents = [] # estructura que guardará los agentes en la plataforma
        # TODO: El agente se une al anillo de Chord q le corresponde según la plataforma
        self.chord = Chord(hash(self.aid), host, port)
        self.start_serving()
        # se añade el ams al anillo de chord


    def register(self, agent_name, uri, state=0):
        "Registers an agent in the ams"
        aid = AID(agent_name, resolvers=[self.aid])
        ams_desc = AMSAgentDescription(aid, state, uri)
        self.agents.append(ams_desc)
        # self.chord.add(hash(aid), ams_desc.dumps())
        

    def deregister(self, aid):
        "Deregisters an agent in the ams"
        self.chord.delete_key(hash(aid))


    def modify(self, aid, state):
        "Modifies the state of an agent"
        # not important...
        pass

    
    def get_agents(self):
        "Returns all the agens in the platform"
        # TODO: Se supone que busque por el resto de las llaves de chord
        return [ad.aid.name for ad in self.agents]
        # return self.chord.get_values()
        

    def get_local_agents(self):
        "Returns all the agents of the ams"
        return [ad.aid.name for ad in self.agents]
        # return self.chord.get_local_values()

    def search(self, aid):
        "Searchs for the description of an agent in the ams"
        for ad in self.agents:
            if ad.aid == aid:
                return ad
        raise Exception(f'Cannot find the agent {aid.name}')
        # try:
        #     desc = self.chord.get(hash(aid))
        #     return AMSAgentDescription.loads(desc)
        # except:
        #     raise Exception(f'Cannot find the agent {aid}')


    def stop_agent(self, aid):
        "Stops an agent"
        agent = self.get_agent_proxy(aid)
        if agent is None:
            return
        agent.stop()

    
    def restart_agent(self, aid):
        "Resumes the execution of an agent"
        agent = self.get_agent_proxy(aid)
        if agent is None:
            return
        agent.restart()

    
    def end_agent(self, aid):
        "Ends the execution of an agent"
        agent = self.get_agent_proxy(aid)
        if agent is None:
            return
        agent.end()
        
    
    def get_agent_status(self, aid):
        "Gets the state of an agent"
        agent = self.get_agent_proxy(aid)
        if agent is None:
            return
        return agent.get_status()
        

    def get_agent_proxy(self, aid):
        try: 
            print(f'Buscando el agente: {aid.name}')
            agent_desc = self.search(aid)
            print(f'Agente encontrado en el AMS, contactando con el cliente...')
            return Pyro4.Proxy(agent_desc.uri)
        except Exception as e:
            print(e)
        return None


    def execute_agent(self, aid, methods):
        "Excecutes the agent with the requiered aid"
        print('---------------------------------------')
        print(f'Solicitando la ejecución del cliente: {aid.name}')
        agent = self.get_agent_proxy(aid)
        if agent is None:
            print(f'No se pudo encontrar el agent {aid.name} en la plataforma')
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
        print(f'Solicitando la ejecución del cliente: {aid.name}')
        agent = self.get_agent_proxy(aid)
        return self._execute_meth(agent, method, *args)
