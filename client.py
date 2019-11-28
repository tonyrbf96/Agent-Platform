from ams import AMS
from test_agents import *
import socket
import cmd
from utils.aid import AID


class PlatformClient(cmd.Cmd):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = '> '

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
        return ip, port


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

        # TODO: hacer lo necesario para inicializar la plataforma...
        self.ams = AMS(ip, port, '')


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
            self.ams.execute_agent(aid, methods)
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
        plataform = params[-1]
        try:
            if args:
                res = self.ams.execute_method(aid, method, *args)
            else:
                res = self.ams.execute_method(aid, method)
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

        Agentes Disponibles: dummy, fibonacci, prime, binary
        """
        try:
            agent_name = args.split()[0]
        except IndexError:
            print('Debe especificar el nombre de un agente')
            return
        try:
            aid = AID(agent_name)
        except ValueError:
            print('El nombre del agente tiene que tener el formato localname@ip:port')
            return

        ams_uri = input('uri del ams: ') #jnjcnkd

        if aid.localname == 'dummy':
            agent = DummyAgent(aid)
        elif aid.localname == 'fibonacci':
            agent = FibonacciAgent(aid)
        elif aid.localname == 'prime':
            agent = PrimeAgent(aid)
        elif aid.localname == 'binary':
            agent = BinaryToDecimalAgent(aid)
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
        try:
            ip, port = self._parse_address(address1)
        except Exception as e:
            print(e)
            return
        ams = AMS(ip, port, address2)
        # TODO: anadir el ams a chord
        

    def do_get_agents(self, args):
        """
        Obtiene el nombre de todos los agentes en la plataforma
        Parámetros:
            - address (opcional): la dirección de la plataforma en la que se añadirá el agente.
                Si no se especifica, se usa la plataforma local de haberse creado, en caso contrario da error.
        """
        agents = self.ams.get_agents()
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
        agents = self.ams.get_local_agents()
        print('Agents in the platform:')
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


if __name__ == "__main__":
    platform = PlatformClient()
    platform.cmdloop()