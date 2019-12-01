

from chord.node import Node
# from chord.node import Node
from utils import aid


class Chord:
    'Interface for handle chord ring'
    def __init__(self, id_, ip, port):
        for i in range(1, 1023 - port):
            try:
                self.node = Node(id_, ip, port + i) 
                break
            except:
                raise Exception('Se falló asignando la dirección')
        

    def __del__(self):
        'kill local node and release resources'
        pass 
    
    def add(self, key, value):
        "add a new data into the chord ring"
        self.node.save(key, value)


    def get(self, key):
        'get value of a key located in Chord ring'
        pass
    

    def get_local_values(self):
        'get local node values'
        pass


    def get_values(self):
        'gets all the values stored in the ring'


    def delete_key(self, key):
        'deletes a given key'
        pass

