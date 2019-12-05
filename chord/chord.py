from node import Node
import debug.logger as log


class Chord:
    'Interface for handle chord ring'

    def __init__(self, id, ip, port, chord_id):
        self.node = Node(id, ip, port, chord_id)

    def __del__(self):
        'kill local node and release resources'
        del(self.node)

    def get(self, key: int):
        'get value of a key located in Chord ring'
        self.node.load(key)

    def get_locals(self):
        'get local node values'
        return self.node.get_data()

    def get_all(self,condition = lambda v:True):
        'gets all the values stored in the ring'
        for data in self.node.iter(lambda node: node.get_data()):
            yield filter(condition,data)

    def get_first(self,condition = lambda v:True):
        'gets a random value from the chord ring'
        for data in self.get_all_values():
            for v in data:
                if condition(v):
                    return v

    def storage(self, key: int, value):
        "add a new key,value into the chord ring"
        self.node.save(key, value)

    def remove(self, key: int):
        'deletes a given key'
        self.node.delete(key)

    def join(self, uri):
        'joins this node to a chord ring using this node (really only one node)'
        self.node.start_serving(uri=uri)
