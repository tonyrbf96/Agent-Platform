import hashlib
from chord_settings import M
from address import Address
import asyncio



class Node:
    def __init__(self,address:Address,m:int):
        self.id = hash(address)
        self.finger = [None for _ in range(0,m)]

    # seft's successor
    @property
    def successor(self) -> 'Node':
        return self.finger[1]

    #ask node self to find id's successor
    def find_successor(self,id:int) -> 'Node':
        p =  self.find_predeccessor(id)
        return  p.successor

    # ask node self to find id's precessor
    def find_predeccessor(self,id:int) -> 'Node':
        node = self
        while node.id < id <= node.successor.id:
            node =  node.closet_preceding_finger(id)
        return node

    # return closest finger preceding id
    def closet_preceding_finger(self,id:int) -> 'Node':
        for i in range(M,1):
            if self.id < self.finger[i].id < id:
                return self.finger[i]
        return self

    # node self joins the network
    # 'node' is a arbitrary node in the network
    ''' # old implementation, bad performance
    def join(self, node: 'Node'):
        if node != None:
            self.init_finger_table(node)
            self.update_others()
            #TODO: Move keys in (predecessor,self) from successor
        else: # self is the only node in the network
            for i in range(1,M):
                self.finger[i] = self
            self.predecessor = self
    '''
    def join(self, node: 'Node'):
        self.predecessor = None
        self.successor = node.find_successor(self.id)
    
    #periodically verify self's inmediate succesor and tell the successor about n
    def stabilize(self):
        x = self.successor.predecessor
        if self.id < x.id < self.successor.id:
            self.successor = self
        successor.notify(self)

    def notify(self,node:'Node'):
        if self.predecessor or self.predecessor.id < node.id < self.id:
            self.predecessor = node

    
    # initialize finger table of local node 
    # 'node' is an arbitrary node already in the network 
    def init_finger_table(self,node: 'Node'):
        self.finger[1] = node.find_successor(self.id)
        self.predecessor = self.successor.predecessor
        self.successor.predecessor = self #send remote call to update predecessor
        for i in range(1,M-1):
            if self.id <= self.finger[i+1].id <= self.finger[i].id:
                self.finger[i+1] = self.finger[i]
            else:
              self.finger[i+1] = node.find_successor(self.finger[i+1].id)

    #update all nodes whose finger tables should refer to n
    def update_others(self):
        for i in range(1,M):
            # find last node p whose i-esime finger might be n
            p = self.find_predeccessor(self.id - 2**(i-1))
            p.update_finger_table(self.id,i)

    # if s i-esime  ith finger of n, update n's finger table with s
    def update_finger_table(self,s:'Node',i:int):
        if self.id <= s.id <= self.finger[i].id:
            self.finger[i] = s
            p = self.predecessor # get first node preceding n
            p.update_finger_table(s,i)

    

node = Node(Address("",1),10)
print(node.successor)
print(node.finger)
