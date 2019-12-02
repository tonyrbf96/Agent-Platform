from node import Node,NodeInfo
import sys
if __name__ =='__main__':
    
    id = sys.argv[1]
    ip = sys.argv[2]
    port = sys.argv[3]
    
    node = Node(int(id),ip,int(port))
    
    id = sys.argv[4]
    ip = sys.argv[5]
    port = sys.argv[6]
    
    node.start_serving(NodeInfo(int(id),ip,int(port)))
    
    while node:
        pass