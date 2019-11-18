from chord_settings import M
from address import Address
import random


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
    def join(self, node: 'Node'):
        self.predecessor = None
        self.successor = node.find_successor(self.id)
    
    #periodically verify self's inmediate succesor and tell the successor about self
    def stabilize(self):
        x = self.successor.predecessor
        if self.id < x.id < self.successor.id:
            self.successor = self
        self.successor.notify(self)

    # node think is might be our predecessor
    def notify(self,node:'Node'):
        if self.predecessor or self.predecessor.id < node.id < self.id:
            self.predecessor = node

    # periodically refresh finger table entries
    def fix_fingers(self):
        i = random.randrange(1,M)
        self.finger[i] = self.find_successor(self.finder[i].id)  

    

    

    

    

node = Node(Address("",1),10)
print(node.successor)
print(node.finger)
