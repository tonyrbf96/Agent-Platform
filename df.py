from agent import BaseAgent
from utils.aid import AID

class DF(BaseAgent):
    def __init__(self, host, port):
        self.aid = AID(f'ams@{host}:{port}')
        self.agents = []

    def register(self, aid, state=0):
        "Registers an agent in the df"
        pass

    def deregister(self, aid):
        "Deregisters an agent in the df"
        pass

    def get_functionality(self, aid):
        "Searches for the functionality of an agent in the ams"
        pass

    def search(self, functionality):
        "Searches for all the agents that implement the required functionality"
        pass
