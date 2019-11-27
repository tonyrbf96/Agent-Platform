import Pyro4
from agent import Agent
from behaviour import Behaviour
from ams import AMS
import time

class DummyAgent(Agent):
    class MyBehav(Behaviour):
        def on_start(self):
            print('Iniciando servicio...')
            self.counter = 0

        def run(self):
            self.counter = 1
            while True:
                print(f'Contador: {self.counter}')
                self.counter +=1
                time.sleep(1)

        def on_end(self):
            self.counter = 0

    class OtherBehav(Behaviour):
        def run(self):
            print('HI!!')

    def setup(self):
        print('------------------------------')
        print('Iniciando el agente Dummy...')
        self.add_behaviour(self.MyBehav('behaviour1'))
        self.add_behaviour(self.OtherBehav('behaviour2'))


class FibonacciAgent(Agent):
    class FiboBehav(Behaviour):
        def run(self, n):
            print('HI')
            try: 
                n = int(n)
            except ValueError:
                raise Exception('Por favor, inserte un argumento válido')
            
            def fibonacci(n):
                if n < 2:
                    return n
                return fibonacci(n-1) + fibonacci(n-2)
            
            res = fibonacci(n)
            print(f'El número {n} de la sucesión de Fibonacci es {res}')

    def setup(self):
        print('---------------------------')
        print('Iniciando el agente Fibonacci...')
        self.add_behaviour(self.FiboBehav('fibonacci'))


class PrimeAgent(Agent):
    class IsPrimeBehav(Behaviour):
        def run(self, n):
            try:
                n  = int(n)
            except ValueError:
                raise Exception('Por favor, inserte un argumento válido.')
            if n == 1:
                print(f'El número {n} es primo')
            for i in range(1, int(n/2)):
                if n % i == 0:
                    print(f'El número {n} no es primo')
                    return
            print(f'El número {n} es primo')   

    def setup(self):
        print('--------------------------')
        print('Iniciando el agente Prime...') 
        self.add_behaviour(self.IsPrimeBehav('is_prime'))    


class BinaryToDecimalAgent(Agent):
    class ConvertToDecimal(Behaviour):
        def run(self, string):
            dec = 0
            for i in range(len(string)):
                d = int(string[i])
                dec = dec * 2 + d
            print(f'El número en decimal de {string} es {dec}')
    
    def setup(self):
        print('--------------------------')
        print('Iniciando el agente BinaryToDecimal...') 
        self.add_behaviour(self.ConvertToDecimal('convert_to_dec'))
