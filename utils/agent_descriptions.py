import json
from utils.aid import AID

# TODO: Use a custom decoder
class AMSAgentDescription:
    def __init__(self, aid, state, services, uri):
        self.aid = aid
        self.current_state = state
        self.uri = uri
        self.services = services

    def change_to_state(self, state):
        self.current_state = state

    def dumps(self):
        return json.dumps({
            'aid': self.aid.name, 
            'state': self.current_state,
            'uri': self.uri,
            'services': self.services})

    @staticmethod
    def loads(obj):
        info = json.loads(obj)
        info['aid'] = AID(info['aid'])
        return AMSAgentDescription(**info)

class DFAgentDescription:
    def __init__(self, aid, services):
        self.aid = aid
        self.services = services