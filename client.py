from ams import AMS
from test_agents import *
from agent_platform import get_platform, initialize_servers, initialize_server
import socket
import cmd
from utils.aid import AID
import Pyro4

class PlatformClient(cmd.Cmd):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = '> '
        self.platform = None


    def _parse_address(self, args):
        "Parses an address, it returns ip, port if successfull, otherwise raises an error"
        try:
            ip, port = args.split(':')
        except ValueError:
            raise Exception('La dirección debe tener el formato ip:port')
        try:
            port = int(port)
        except ValueError:
            raise Exception('El puerto debe ser un número válido')
        try:
            self._check_ip(ip)
        except:
            raise TypeError(f'El formato del ip {ip} es incorrecto')            
      
        return ip, port


    def _check_ip(self, ip):
        "Checks a valid ip"
        strings = ip.split('.')
        assert len(strings) == 4
        for s in strings:
            n = int(s)
            assert 0 <= n < 256
        
    
    def _get_ams(self, address):
        "Gets an ams from a given address that represents a platform"    
        ams_uri = self._get_ams_uri(address)
        return Pyro4.Proxy(ams_uri)

    def _get_ams_uri(self, address):
        platform = self._get_platform(address)
        return platform.get_node()

    def _get_platform(self, address):
        "Gets a platform from a given address that represents a platform"
        ip, port = self._parse_address(address)
        return get_platform(ip, port)


    def do_platform(self, args):
        """
        Se comienza la creación de una plataforma (inicializándose varios ams y df)
        Parámetros:
            - address: la dirección de la plataforma (con la forma ip:port)
        """
        try:
            ip, port = self._parse_address(args)
        except Exception as e:
            print(e)
            return
        
        try:
            self.platform = initialize_server(ip, port)
            self.ip, self.port = ip, port
            ams = AMS(ip, port+1, '')
            self.platform.register(ams.aid.name, ams.uri)
            self.platform.add_server()
        except OSError:
            print('No se pudo asignar la dirección pedida')
            return


    def do_add_server(self, args):
        """
        Anade un servidor a una plataforma determinada.
        Parámetros:
            - platform (opcional): dirección de la plataforma en la que se añadirá el agente.
                Si no se especifica, se usa la plataforma local de haberse creado, en caso contrario da error.
        """
        params = args.split()
        try:
            if params:
                address = params[0]
                platform = self._get_platform(address)
            else:
                if not self.platform:
                    print('No se ha creado una plataforma local')
                    return
                platform = self.platform
            platform.add_server()
        except Exception as e:
            print(e)



    def do_execute(self, args):
        """
        Ejecuta los métodos especificados de un agente provisto
        Parámetros:
            - agent: el nombre del agente a ejecutar
            - methods: una lista de métodos separados por espacio
            - platform: dirección de la plataforma en la que se añadirá el agente.
        """
        params = args.split()
        if len(params) < 3:
            print('Faltan parámetros')
            return
        
        agent_name = params[0] 
        try:
            aid = AID(agent_name)
        except ValueError:
            print('El nombre del agente tiene que tener el formato localname@ip:port')
            return
        
        methods = params[1:-1]
        platform = params[-1]
        try:
            ams = self._get_ams(platform)
            ams.execute_agent(aid, methods)
        except Exception as e:
            print(e)


    def do_execute_method(self, args):
        """
        Ejecta un método de un agente provisto
        Parámetros:
            - agent: el nombre del agente a ejecutar.
            - method: el nombre del método a ejecutar.
            - args: una lista de los argumentos del método a ejecutar.
            - platform: dirección de la plataforma en la que se añadirá el agente.
        """
        params = args.split()
        if len(params) < 3:
            print('Faltan parámetros')
            return

        agent_name = params[0]
        try:
            aid = AID(agent_name)
        except ValueError:
            print('El nombre del agente tiene que tener el formato localname@ip:port')
            return

        method = params[1]
        if len(params) > 3:
            args = params[2:-1]
        else:
            args = None
        try:
            ams = self._get_ams(platform)
            if args:
                res = ams.execute_method(aid, method, *args)
            else:
                res = ams.execute_method(aid, method)
            if res is not None:
                print(f'El resultado del método ejecutado es {res}')
        except Exception as e:
            print(e)


    def do_agent(self, args):
        """
        Inicializa un agente y lo registra en un ams.
        Parámetros:
            - agent: el nombre del agente que se inicializará (con el formato localname@ip:port)
            - platform (opcional): dirección de la plataforma en la que se añadirá el agente.
                Si no se especifica, se usa la plataforma local de haberse creado, en caso contrario da error.

        Agentes Disponibles: dummy, fibonacci, prime, binary, echo, hello_world
        """
        params = args.split()
        try:
            agent_name = params[0]
        except IndexError:
            print('Debe especificar el nombre de un agente')
            return
        try:
            aid = AID(agent_name)
        except ValueError:
            print('El nombre del agente tiene que tener el formato localname@ip:port')
            return
        
        try:
            if len(params) > 1:
                address = params[1]
                ams_uri = self._get_ams_uri(address)
            else:
                if not self.platform:
                    print('No se ha creado una plataforma local')
                    return
                ams_uri  = self.platform.get_node()
        except Exception as e:
            print(e)
            return
        
        # ams_uri = input('uri del ams: ') #jnjcnkd

        if aid.localname == 'dummy':
            agent = DummyAgent(aid)
        elif aid.localname == 'fibonacci':
            agent = FibonacciAgent(aid)
        elif aid.localname == 'prime':
            agent = PrimeAgent(aid)
        elif aid.localname == 'binary':
            agent = BinaryToDecimalAgent(aid)
        elif aid.localname == 'echo':
            agent = EchoAgent(aid)
        elif aid.localname == 'hello_world':
            agent = HelloWorldAgent(aid)
        else:
            print('No se encuentra el agente solicitado')
            return
        
        agent.register_ams(ams_uri)
    

    def do_ams(self, args):
        """
        Anade un nuevo ams a la plataforma
        Parámetros:
            - address1: la dirección del nuevo ams
            - address2 (opcional): la dirección de la plataforma en la que se añadirá el agente.
                Si no se especifica, se usa la plataforma local de haberse creado, en caso contrario da error.
        """
        params = args.split()
        if len(params) < 1:
            print('Por favor inserte más argumentos')
        address1 = params[0]
        if len(params) > 1:
            address2 = params[1]
        else:
            if not self.platform:
                print('No se ha creado una plataforma local')
                return
            address2 = f'{self.ip}:{self.port}'
        
        try:
            ip, port = self._parse_address(address1)
        except Exception as e:
            print(e)
            return
        
        try:
            ams = AMS(ip, port, address2)
        except:
            print(f'La dirección {address1} está ocupada')
        try:
            platform = get_platform(self.ip, self.port)
            platform.register(ams.aid.name, ams.uri)
        except Exception as e:
            print(e)
            return
    

    def do_get_agents(self, args):
        """
        Obtiene el nombre de todos los agentes en la plataforma
        Parámetros:
            - address (opcional): la dirección de la plataforma en la que se añadirá el agente.
                Si no se especifica, se usa la plataforma local de haberse creado, en caso contrario da error.
        """
        params = args.split()
        if params:
            platform = params[0]
        else:
            if not self.platform:
                print('No se ha creado una plataforma local')
                return
            platform = f'{self.ip}:{self.port}'
            
        try:
            ams = self._get_ams(platform)
        except Exception as e:
            print(e)
            return

        agents = ams.get_agents()
        print('Agents in the platform:', end=' ')
        for a in agents:
            print(a, end=' ')
        print()


    def do_get_ams_agents(self, args):
        """
        Obtiene el nombre de los agentes registrados en un ams especifico
        Parámetros:
            - address1: la dirección del ams
            - address2 (opcional): la dirección de la plataforma en la que se añadirá el agente.
                Si no se especifica, se usa la plataforma local de haberse creado, en caso contrario da error.
        """
        params = args.split()
        if not params:
            print('Por favor inserte más argumentos')
            return
        
        address1 = params[0]
        try:
            ip, port = self._parse_address(address1)
        except Exception as e:
            print(e)
            return   

        if len(params) > 1:
            address2 = params[1]
            try:
                ip2, port2 = self._parse_address(address2)
                platform = get_platform(ip2, port2)
            except Exception as e:
                print(e)
        else:
            if not self.platform:
                print('No se ha creado una plataforma local')
                return
            platform = self.platform
            
        try:
            ams_uri = platform.get_item(f'ams@{ip}:{port}')
            ams = Pyro4.Proxy(ams_uri)
        except Exception as e:
            print(e)
            return

        agents = ams.get_local_agents()
        print('Agents in the ams:', end='\n\t')
        for a in agents:
            print(a, end=' ')
        print()


    def do_get_service_agent(self, args):
        """
        Obtiene un agente que cumple determinado servicio
        Parámetros:
            - service_name: Nombre del servicio que se solicita
            - platform (opcional): dirección de la plataforma en la que se añadirá el agente.
                Si no se especifica, se usa la plataforma local de haberse creado, en caso contrario da error.
        """
        pass


    def do_execute_service(self, args):
        """
        Ejecuta un servicio determinado en una plataforma
        Parámetros:
            - service_name: Nombre del servicio que se solicita
            - platform (opcional): dirección de la plataforma en la que se añadirá el agente.
                Si no se especifica, se usa la plataforma local de haberse creado, en caso contrario da error.
        """
        pass


    def get_services(self, args):
        """
        Obtiene todos los servicios disponibles en la plataforma
        Parámetros:
            - platform (opcional): dirección de la plataforma en la que se añadirá el agente.
                Si no se especifica, se usa la plataforma local de haberse creado, en caso contrario da error.
        """
        pass


    def do_quit(self, args):
        "Stops the execution of the prompt"
        return True

if __name__ == "__main__":
    platform = PlatformClient()
    platform.cmdloop()