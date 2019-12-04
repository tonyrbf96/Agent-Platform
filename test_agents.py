from agent import Agent
from behaviour import Behaviour, run_cyclic
from ams import AMS
import time
import threading

class HelloWorldAgent(Agent):
    class HelloBehav(Behaviour):
        def run(self):
            print('Hello World!')
    
    def setup(self):
        print('---------------------------------')
        print('Iniciando el agente Hello World...')
        self.add_behaviour('hello_world', self.HelloBehav)


class EchoAgent(Agent):
    class EchoBehav(Behaviour):
        @run_cyclic
        def run(self):
            text = input()
            print(text)

    def setup(self):
        print('---------------------------------')
        print('Iniciando el agente Echo...')
        self.add_behaviour('echo', self.EchoBehav)


class DummyAgent(Agent):
    class MyBehav(Behaviour):
        def on_start(self):
            self.counter = 1

        @run_cyclic
        def run(self):
            print(f'Contador: {self.counter}')
            self.counter +=1
            time.sleep(1)

    class OtherBehav(Behaviour):
        def run(self):
            print('HI!!')

    def setup(self):
        print('------------------------------')
        print('Iniciando el agente Dummy...')
        self.add_behaviour('behaviour1', self.MyBehav)
        self.add_behaviour('behaviour2', self.OtherBehav)


class FibonacciAgent(Agent):
    class FiboBehav(Behaviour):
        def run(self, n):
            print('HI')
            try: 
                n = int(n)
            except ValueError:
                raise Exception('Por favor, inserte un argumento válido')
            
            def fibonacci(n):
                if self.ended: return
                if self.stopped: self.lock.acquire()
                if n < 2:
                    return n
                return fibonacci(n-1) + fibonacci(n-2)
            
            res = fibonacci(n)
            print(f'El número {n} de la sucesión de Fibonacci es {res}')

    def setup(self):
        print('---------------------------')
        print('Iniciando el agente Fibonacci...')
        self.add_behaviour('fibonacci', self.FiboBehav)


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
                if self.ended: return
                if self.stopped: self.lock.acquire()

                if n % i == 0:
                    print(f'El número {n} no es primo')
                    return
            print(f'El número {n} es primo')   

    def setup(self):
        print('--------------------------')
        print('Iniciando el agente Prime...') 
        self.add_behaviour('is_prime', self.IsPrimeBehav)    


class BinaryToDecimalAgent(Agent):
    class ConvertToDecimal(Behaviour):
        def run(self, string):
            dec = 0
            for i in range(len(string)):
                if self.ended: return
                if self.stopped: self.lock.acquire()

                d = int(string[i])
                dec = dec * 2 + d
            print(f'El número en decimal de {string} es {dec}')
    
    def setup(self):
        print('--------------------------')
        print('Iniciando el agente BinaryToDecimal...') 
        self.add_behaviour('binary_to_decimal', self.ConvertToDecimal)

