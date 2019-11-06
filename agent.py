
# Agents states
INITIATED = 0   # The Agent object is built, but hasn't registered itself yet with the AMS, has neither a name nor an address and cannot communicate with other agents.
ACTIVE = 1      # The Agent object is registered with the AMS, has a regular name and address and can access all the various JADE features.
SUSPENDED = 2   # The Agent object is currently stopped. Its internal thread is suspended and no agent behaviour is being executed
WAITING = 3     # The Agent object is blocked, waiting for something. Its internal thread is sleeping and will wake up when some condition is met (typically when a  message arrives).
DELETED = 4     # The Agent is definitely dead. The internal thread has terminated its execution and the Agent is no more registered with the AMS. 


class BaseAgent:
    def __init__(self, aid, mts):
        self.aid = aid
        self.behaviours = []
        self.mts = mts
        self.name = aid.name
        self.state = INITIATED

    def listen(self):
         "Listens for incomming message reception"
         pass

    def react(self, message):
        """Will be executed all the times the agent
        receives any type of data
        """
        pass

    def receive():
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

    def excute(self):
        "Executes an agent behaviour"
        print(f'Agent {self.name} starts execution')
        msg = self.receive()
        if msg is not None:
            # excecutes the required behaviour of the agent
            pass


    # def inform(self, angents, data):
    #     "Handles the performative inform"
    #     pass

    # def request(self, agents, data):
    #     "Handles the perfomative request"
    #     pass

    # def inform_if(self, agents, data):
    #     "Handles the perfomative inform_if"
    #     pass

    # def refuse(self, agents, data):
    #     "Handles the perfomative refuse"
    #     pass


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