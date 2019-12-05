from chord import Chord
import sys
import signal



chord = None

def quit():
    global chord
    print(f"\n>>> quit")
    del(chord)

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
    
    
    chord = Chord(int(id),ip,int(port),'C-1')
    
    #id ip port for join point Node
    
    if len(sys.argv)>5:
        id = sys.argv[4]
        ip = sys.argv[5]
        port = sys.argv[6]
        chord.join(chord.node.URI(int(id),ip,int(port)))
    else:
        uri = sys.argv[4]
        chord.join(uri=uri)
    #this try is because when delete node the while raise an exception, this is when I kill this process
    try: 
        while chord:
            command = input('>>> ')
            
            if command == 'quit':
                sys.quit()
            if command == 'locals':
                print(list(chord.get_locals()))
            if command == 'all':
                for values in chord.get_all():
                     print(list(values))
            if command.startswith('add'):
                keys = command.split()
                for key in keys[1:]:
                    chord.storage(int(key),f'{int(key)}')
            # if command == 'debug':
            #     print(node.__dict__)
            if command.startswith('delete'):
                keys = command.split()
                for key in keys[1:]:
                    chord.remove(int(key))
            if command == 'uri':
                print(chord.node.URI(chord.node.id,chord.node.ip,chord.node.port))
            pass
    except:
        pass
    
    