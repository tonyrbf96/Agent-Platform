from utils.acl_message import ACLMessage

import json

class MTS:
    def __init__(self):
        pass

    def aid_msg(self, name, adresses=None, resolvers=None):
        return {'name': name, 
                'adresses': adresses, 
                'resolvers': resolvers}

    def register_agent_ams(self, aid, ams):
        msg = ACLMessage()
        msg.add_receiver(ams)
        msg.sender = aid.get_aid_dict()
        return msg.get_msg()

    def execute_agent(self, sender, receivers, content):
        msg = ACLMessage()
        msg.add_receiver()
    