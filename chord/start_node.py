from node import Node,NodeInfo
import sys
import signal



node = None

def quit():
    global node
    print(f"\n>>> quit")
    del(node)

def receiveSignal(signalNumber, frame):
    quit()

if __name__ =='__main__':

    # set signal listeners for secure close daemons
    signal.signal(signal.SIGINT, receiveSignal)
    signal.signal(signal.SIGQUIT, receiveSignal)
    signal.signal(signal.SIGTERM, receiveSignal)
    signal.signal(signal.SIGABRT, receiveSignal)

   
    #id ip port of Node
    id = sys.argv[1]
    ip = sys.argv[2]
    port = sys.argv[3]
    
    
    node = Node(int(id),ip,int(port))
    
    #id ip port for join point Node
    id = sys.argv[4]
    ip = sys.argv[5]
    port = sys.argv[6]
    
    node.start_serving(NodeInfo(int(id),ip,int(port)))
    
    #this try is because when delete node the while raise an exception, this is when I kill this process
    try: 
        while node:
            command = input('>>> ')
            
            if command == 'show':
                node.print_info()
            if command == 'quit':
                sys.quit()
            pass
    except:
        pass
    
    