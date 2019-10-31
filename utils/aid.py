class AID:
    def __init__(self, name:str, addresses:list=None, resolvers:list=None):
        """
        Agent Identifier
        name: localname@address:port
        addresses: 
        """
        self.name = name
        self.localname, address = self.name.split('@')
        self.addresses = [address]
        if ':' in address:
            self.host, self.port = address.split(':')
            self.port = int(self.port)
        else:
            self.host, self.host = None, None

        self.resolvers = resolvers if resolvers else list()

    @staticmethod
    def create_aid(message)
        "Creats an aid from an ACL message"
        pass

    def __hash__(self):
        h = hash(self.name) 
        for i in self.addresses + self.resolvers:
            h += hash(i)
        
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
    agentid1 = AID('agent-b@bar.com', resolvers=[AID('ams@foo.com', ['iiop://foo.com//acc'])])
    print(agentid1)