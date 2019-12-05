import json

def check_ip(ip):
    "Checks a valid ip"
    strings = ip.split('.')
    assert len(strings) == 4
    for s in strings:
        n = int(s)
        assert 0 <= n < 256


class AID:
    def __init__(self, name:str, resolvers:list=None):
        """
        Agent Identifier
        name: localname@address:port
        addresses: 
        """
        self.name = name
        self.localname, address = self.name.split('@')
        self.addresses = [address]
        self.host, self.port = address.split(':')
        self.port = int(self.port)
        self.host = check_ip(self.host)

        self.resolvers = resolvers if resolvers else list()


    def get_aid_dict(self):
        "Gets the aid dict format to be passed in the acl message"
        return {
            'name': self.name,
            'addresses': self.addresses,
            'resolvers': self.resolvers  
        }

    def __hash__(self):
        h = hash(self.name) 
        for i in self.addresses + self.resolvers:
            h += hash(i)
        a = ''
        return h
        
    def __eq__(self, other):
        return self.name == other.name

    def __str__(self):
        return self.print_depht(1)

    def print_depht(self, d):
        res = f'(agent-identifier\n' +  '\t'*d + f':name {self.name}'
        if self.addresses:
            res += '\n' + '\t'*d + ':addresses (sequence'
            for i in self.addresses:
                res += ' ' + str(i)
            res += ')'
        if self.resolvers:
            res += '\n' + '\t'*d +':resolvers (sequence'
            for i in self.resolvers:
                res += ' ' + i.print_depht(d+1) 
            res += ')'
        res += '\n' + '\t'*(d-1) + ')'
        return res

    def __repr__(self):
        return self.name
        

    
if __name__ == "__main__":
    agentid1 = AID('agent-b@127.0.0.1:9000', resolvers=[AID('ams@foo.com', ['iiop://foo.com//acc'])])
    print(agentid1)