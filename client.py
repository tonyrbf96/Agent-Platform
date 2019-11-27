from ams import AMS
from test_agents import *
import socket
import cmd


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
        self.ams = AMS(ip, port)


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
        methods = params[1:-1]
        platform = params[-1]
        try:
            self.ams.execute_agent(agent_name, methods)
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
        if len(params) < 4:
            print('Faltan parámetros')
            return

        agent_name = params[0]
        method = params[1]
        args = params[2:-1]
        plataform = params[-1]
        try:
            res = self.ams.execute_method(agent_name, method, *args)
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
            localname, address = agent_name.split('@')
            ip, port = address.split(':')
        except ValueError:
            print('El nombre del agente tiene que tener el formato localname@ip:port')
            return

        ams_uri = input() #jnjcnkd

        if localname == 'dummy':
            agent = DummyAgent(agent_name)
        elif localname == 'fibonacci':
            agent = FibonacciAgent(agent_name)
        elif localname == 'prime':
            agent = PrimeAgent(agent_name)
        elif localname == 'binary':
            agent = BinaryToDecimalAgent(agent_name)
        else:
            print('No se encuentra el agente solicitado')
            return
        agent.register_ams(ams_uri)
    

    def do_ams(self, address):
        """
        Anade un nuevo ams a la plataforma
        Parámetros:
            - address1: la dirección del nuevo ams
            - address2 (opcional): la dirección de la plataforma en la que se añadirá el agente.
                Si no se especifica, se usa la plataforma local de haberse creado, en caso contrario da error.
        """
        try:
            ip, port = self._parse_address(address)
        except Exception as e:
            print(e)
            return
        ams = AMS(ip, port)
        # TODO: anadir el ams a chord
        


if __name__ == "__main__":
    platform = PlatformClient()
    platform.cmdloop()