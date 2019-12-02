
from node import Node

class Chord:
    'Interface for handle chord ring'
    def __init__(self, id:int,ip:str,port:int):
        
        pass
    
    def __del__(self):
        'kill local node and release resources'
        pass 
    
    def add(self, key, value):
        "add a new data into the chord ring"
        pass


    def get(self, key):
        'get value of a key located in Chord ring'
        pass

    def get_values(self):
        'get local node values'
        pass


    def delete_key(self, key):
        'deletes a given key'
        pass

