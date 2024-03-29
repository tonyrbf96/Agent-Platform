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
    
    
    node = Node(int(id),ip,int(port),'boostrap')
    
    #id ip port for join point Node
    
    if len(sys.argv)>5:
        id = sys.argv[4]
        ip = sys.argv[5]
        port = sys.argv[6]
        node.start_serving(NodeInfo(int(id),ip,int(port)))
    else:
        uri = sys.argv[4]
        node.start_serving(uri=uri)
    #this try is because when delete node the while raise an exception, this is when I kill this process
    try: 
        while node:
            command = input('>>> ')
            
            if command == '' or command == 'show':
                node.print_info()
            if command == 'quit':
                sys.quit()
            if command.startswith('save'):
                keys = command.split()
                for key in keys[1:]:
                    node.save(int(key),'')
            if command == 'debug':
                print(node.__dict__)
            if command.startswith('delete'):
                keys = command.split()
                for key in keys[1:]:
                    node.delete(int(key))
            if command == 'uri':
                print(node.URI(node.id,node.ip,node.port))
            pass
    except:
        pass
    
    