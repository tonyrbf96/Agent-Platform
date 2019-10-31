class AgentPlatform:
    def __init__(self):
        self.agents = []
        self.ams = []
        self.df = []
        self.mts = None

    def listen_petitions(self):
        "Listens for all the petitions of agents in the platform"
        pass

    def add_agent(self, aid):
        'Adds an agent in the platform'
        pass

    def add_ams(self, aid):
        "Adds a new ams agent in the platform"
        pass

    def add_df(self, aid):
        "Adds a new df agent in the platform"
        pass

    def get_operation(self, message):
        "Gets whats the operation especified in the given message"
        pass

    