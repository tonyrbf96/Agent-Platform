from ams import AMS, get_ams, get_ams_uri, get_ams_fixed_uri
from test_agents import *
# from agent_platform_v1 import get_platform, initialize_server, add_server
import socket
import cmd
from utils.aid import AID, check_ip
import Pyro4
from random import randint
import json

class PlatformClient(cmd.Cmd):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.prompt = '> '
        self.ip, self.port = None, None
        self.ams = None

    def do_EOF(self):
        return

    def emptyline(self):
        return

    def _parse_address(self, args):
        "Parses an address, it returns ip, port if successfull, otherwise raises an error"
        try:
            ip, port = args.split(':')
        except:
            raise Exception('La dirección debe tener el formato ip:port')
        try:
            port = int(port)
        except ValueError:
            raise Exception('El puerto debe ser un número válido')
        try:
            assert 0 <= port <= 65535
        except AssertionError:
            raise Exception('El puerto debe ser un número entre 0-65535')
        try:
            check_ip(ip)
        except:
            raise TypeError(f'El formato del ip {ip} es incorrecto')            
      
        return ip, port

    def _get_identifier(self, address):
        ip, port = self._parse_address(address)
        return f'ams_{ip}:{port}'

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
            self.ip, self.port = ip, port
            self.id = 'ams_' + f'{ip}:{port}'
            self.ams = AMS(ip, port, self.id)
            self.ams.join()
        except OSError:
            print('No se pudo asignar la dirección pedida')



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
        identifier = self._get_identifier(platform)
        try:
            ams = get_ams(identifier)
            ams.execute_agent(aid, methods)
        except Exception as e:
            print(e)


    def do_execute_method(self, args):
        """
        Ejecuta un método de un agente provisto
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

        identifier = self._get_identifier(params[-1])
        try:
            ams = get_ams(identifier)
            ams.ping()
        except:
            print('Fallo al contactar con el servidor del ams')
            return
        try:
            if args:
                res = ams.execute_method(aid, method, *args)
            else:
                res = ams.execute_method(aid, method)
        except Exception as e:
            print(e)


    def change_agent_status(self, args):
        "Helper function to change the status stop, restart or end an agent"
        params = args.split()
        try:
            agent_name = params[0]
        except IndexError:
            print('Debe especificar el nombre de un agente.')
            return None, None
       
        try:
            aid = AID(agent_name)
        except ValueError:
            print('El nombre del agente tiene que tener el formato localname@ip:port')
            return None, None


        try:
            if len(params) > 1:
                id_ = params[1]
            else:
                if not self.ip:
                    print('No se ha creado una plataforma local')
                    return
                id_ = f'{self.ip}:{self.port}'
            id_ = self._get_identifier(id_) 
            ams_uri = get_ams_uri(id_)
        except Exception as e:
            print(e)
            return None, None
        
        return ams_uri, aid 

   
    def do_stop_agent(self, args):
        """
        Para la ejecución de un agente en una plataforma determinada
        Parámetros:
            - agent: el nombre del agente que se inicializará (con el formato localname@ip:port)
            - platform (opcional): dirección de la plataforma en la que se anadirá el agente.
                Si no se especifica, se usa la plataforma local de haberse creado, en caso contrario da error.
        """
        ams_uri, aid = self.change_agent_status(args)
        if ams_uri is None or aid is None:
            return

        try:
            ams = Pyro4.Proxy(ams_uri)
            ams.stop_agent(aid)
        except Exception as e:
            print(e)


    def do_restart_agent(self, args):
        """
        Resume la ejecución de un agente en una plataforma determinada
        Parámetros:
            - agent: el nombre del agente que se inicializará (con el formato localname@ip:port)
            - platform (opcional): dirección de la plataforma en la que se anadirá el agente.
                Si no se especifica, se usa la plataforma local de haberse creado, en caso contrario da error.
        """
        ams_uri, aid = self.change_agent_status(args)
        if ams_uri is None or aid is None:
            return

        try:
            ams = Pyro4.Proxy(ams_uri)
            ams.restart_agent(aid)
        except Exception as e:
            print(e)


    def do_end_agent(self, args):
        """
        Termina la ejecución de un agente en una plataforma determinada
        Parámetros:
            - agent: el nombre del agente que se inicializará (con el formato localname@ip:port)
            - platform (opcional): dirección de la plataforma en la que se anadirá el agente.
                Si no se especifica, se usa la plataforma local de haberse creado, en caso contrario da error.
        """
        ams_uri, aid = self.change_agent_status(args)
        if ams_uri is None or aid is None:
            return

        try:
            ams = Pyro4.Proxy(ams_uri)
            ams.end_agent(aid)
        except Exception as e:
            print(e)


    def do_agent_status(self, args):
        """
        Obtiene el estado de un agente en una plataforma determinada
        Parámetros:
            - agent: el nombre del agente que se inicializará (con el formato localname@ip:port)
            - platform (opcional): dirección de la plataforma en la que se anadirá el agente.
                Si no se especifica, se usa la plataforma local de haberse creado, en caso contrario da error.
        """
        ams_uri, aid = self.change_agent_status(args)
        if ams_uri is None or aid is None:
            return

        try:
            ams = Pyro4.Proxy(ams_uri)
            status = ams.get_agent_status(aid)
            if status == 1:
                print(f'El agente {aid.name} está activo')
            elif status == 2:
                print(f'El agente {aid.name} está ejecutando al menos un servicio')
            elif status == 3:
                print(f'El agente {aid.name} tiene servicios detenidos')
            elif status == 4:
                print(f'El agente {aid.name} está caído')
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
                id_ = self._get_identifier(params[1])
                ams_uri = get_ams_uri(id_) 
            else:
                if not self.ams:
                    print('No se ha creado una plataforma local')
                    return
                ams_uri = self.ams.uri
        except Exception as e:
            print(e)
            return
        
        try:
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
        except Exception as e:
            return

        try:
            agent.register_ams(ams_uri)
        except Exception as e:
            print(e)


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
        try:
            if len(params) > 1:
                address2 = params[1]
                id_ = self._get_identifier(params[1])
                register_ams_uri = get_ams_uri(id_) 
            else: 
                if not self.ams:
                    print('No se ha creado una plataforma local')
                    return
                id_ = self.id
                address2 = f'{self.ip}:{self.port}'
                register_ams_uri = self.ams.uri
            ip, port = self._parse_address(address1)
        except Exception as e:
            print(e)
            return
        
        try:
            ams = AMS(ip, port, 'ams_' + address2)
        except:
            print(f'La dirección {address1} está ocupada')
            return
        try:
            ams.join(register_ams_uri)
        except Exception as e:
            print(e)   

    def do_get_agents(self, args):
        """
        Obtiene el nombre de todos los agentes en la plataforma
        Parámetros:
            - address (opcional): la dirección de la plataforma en la que se añadirá el agente.
                Si no se especifica, se usa la plataforma local de haberse creado, en caso contrario da error.
        """
        params = args.split()
        try:
            if params:
                id_ = params[0]
            else:
                if not self.ip:
                    print('No se ha creado una plataforma local')
                    return
                id_ = f'{self.ip}:{self.port}'
            id_ = self._get_identifier(id_)
            ams = get_ams(id_)
        except Exception as e:
            print(e)
            return

        agents = ams.get_agents()
        print('Agents in the platform:')
        for a in agents:
            print('\t', a)
        print()


    def do_get_ams_agents(self, args):
        """
        Obtiene el nombre de los agentes registrados en un ams específico
        Parámetros:
            - address1: la dirección del ams
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

        try:
            ams_uri = get_ams_fixed_uri(ip, port)
            if not ams_uri:
                raise Exception('No se pudo encontrar el ams en la plataforma')    
            ams = Pyro4.Proxy(ams_uri)
            agents = ams.get_local_agents()
        except Exception as e:
            print(e)
            return

        print('Agents in the ams:')
        for a in agents:
            print('\t', a)


    def _get_agents_by_service(self, args):
        'Auxiliar method to search for the agents that have some service'
        params = args.split()
        if not params:
            print('Introduzca más arguementos')
            return
        service_name = params[0]
        
        if len(params) > 1:
            id_ = self._get_identifier(params[1])
            ams_uri =  get_ams_uri(id_)
        else:
            if not self.ams:
                print('No se ha creado ninguna plataforma local')
                return
            ams_uri = self.ams.uri
        return ams_uri, service_name


    def do_get_agents_by_service(self, args):
        """
        Obtiene un agente que cumple determinado servicio
        Parámetros:
            - service_name: Nombre del servicio que se solicita
            - platform (opcional): dirección de la plataforma en la que se añadirá el agente.
                Si no se especifica, se usa la plataforma local de haberse creado, en caso contrario da error.
        """
        try:
            ams_uri, service_name = self._get_agents_by_service(args)
            with Pyro4.Proxy(ams_uri) as ams:
                agents = list(ams.search_service(service_name))
            if not agents:
                print('No existe ningún agente con el servicio solicitado.')
            else:
                print('Agentes con el servicio solicitado:')
                for a in agents:
                    print('\t', a)
        except Exception as e:
            print(e)


    def do_execute_service(self, args):
        """
        Ejecuta un servicio determinado en una plataforma
        Parámetros:
            - service_name: Nombre del servicio que se solicita
            - platform: dirección de la plataforma en la que se añadirá el agente.
                Si no se especifica, se usa la plataforma local de haberse creado, en caso contrario da error.
        """
        params = args.split()
        try:
            ams_uri, service_name = self._get_agents_by_service(args)
            with Pyro4.Proxy(ams_uri) as ams:
                agent = ams.search_agent_by_service(service_name)
            agent = json.loads(agent)
            if not agent:
                print('No existe ningún agente con el servicio solicitado.')
            else:
                aid = AID(agent['aid'])
                if len(params) <= 2:
                    ams.execute_method(aid, service_name)
                else:
                    args = params[2:]
                    ams.execute_method(aid, service_name, *args)
        except Exception as e:
            print(e)


    def do_get_services(self, args):
        """
        Obtiene todos los servicios disponibles en la plataforma
        Parámetros:
            - platform (opcional): dirección de la plataforma en la que se añadirá el agente.
                Si no se especifica, se usa la plataforma local de haberse creado, en caso contrario da error.
        """
        params = args.split()
        if params:
            id_ = self._get_identifier(params[0])
            ams = get_ams(id_) 
        else:
            if not self.ams:
                print('No se ha creado una plataforma local')
                return
            ams = self.ams

        agents = ams.get_agents()
        res = [json.loads(a) for a in agents]
        services = set(s for a in res for s in a['services'])

        print('Services in the platform:')
        for s in services:
            print('\t', s)
        print()
        


    def do_quit(self, args):
        "Stops the execution of the prompt"
        return True


if __name__ == "__main__":
    platform = PlatformClient()
    platform.cmdloop()