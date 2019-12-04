import json
from aid import AID

# TODO: Use a custom decoder
class AMSAgentDescription:
    def __init__(self, aid, state, uri):
        self.aid = aid
        self.current_state = state
        self.uri = uri

    def change_to_state(self, state):
        self.current_state = state

    def dumps(self):
        return json.dumps({
            'aid': aid.name, 
            'state': state,
            'uri': uri})

    @staticmethod
    def loads(json_obj):
        info = json.loads(json_obj)
        info['aid'] = AID(info['aid'])
        return AMSAgentDescription(**info)

class DFAgentDescription:
    def __init__(self, aid, services):
        self.aid = aid
        self.services = services

class ServiceDescription:
    "Describes the services that an agent provides"
    def __init__(self, name, type_):
        self.name = name
        self.type = type_