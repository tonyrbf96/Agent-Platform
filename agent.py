class BaseAgent:
    def __init__(self, aid, mts):
        self.aid = aid
        self.behaviours = []
        self.mts = mts

    def listen(self):
         "Listens for incomming message reception"
         pass

    def react(self, message):
        """Will be executed all the times the agent
        receives any type of data
        """
        pass

    def send(self, message):
        """Sends an ACL message to the agents specified
        in the receivers parameter of the ACL message.
        """
        pass

    def suspend(self):
        "Suspends the agent"
        pass

    def end(self):
        "Ends the execution of an agent"
        pass

    def excute(self):
        "Executes an agent behaviour"
        pass

    def inform(self, angents, data):
        "Handles the performative inform"
        pass

    def request(self, agents, data):
        "Handles the perfomative request"
        pass

    def inform_if(self, agents, data):
        "Handles the perfomative inform_if"
        pass

    def refuse(self, agents, data):
        "Handles the perfomative refuse"
        pass


class Agent(BaseAgent):
    def __init__(self, aid, mts):
        super().__init__(aid, mts)
        
    def register_ams(self, ams):
        "Registers the agent in a given ams"
        pass

    def register_df(self, df):
        "Registers the agent in a given df"
        pass


if __name__ == "__main__":
    pass