from agent import BaseAgent
from utils.aid import AID

class AMS(BaseAgent):
    def __init__(self, host, port):
        self.aid = AID(f'ams@{host}:{port}')
        self.agents = [] # estructura que guardará los agentes en la plataforma

    def register(self, aid, state=0):
        "Registers an agent in the ams"
        pass

    def deregister(self, aid):
        "Deregisters an agent in the ams"
        pass

    def modify(self, aid, state):
        "Modifies the state of an agent"
        pass

    def search(self, aid):
        "Searchs for the description of an agent in the ams"
        pass

    def suspend_agent(self, aid):
        "Suspends an agent"
        pass

    def resume_agent(self, aid):
        "Resumes the execution of an agent"
        pass

    def end_agent(self, aid):
        "Finishes the execution of an agent"
        pass

    def create_agent(self):
        "Creates and agent"
        #? Not sure...
        pass

    def execute_agent(self, aid):
        "Excecutes the agent with the requiered aid"
        pass