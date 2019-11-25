from agent import Agent
from behaviour import Behaviour
from ams import AMS


class DummyAgent(Agent):
    class MyBehav(Behaviour):
        def on_start(self):
            print('Starting behaviour...')
            self.counter = 0

        def run(self):
            while self.counter < 10:
                print(f'Counter: {self.counter}')
                self.counter +=1

        def on_end(self):
            self.counter = 0

    class OtherBehav(Behaviour):
        def run(self):
            print('HI!!')

    def setup(self):
        print('------------------------------')
        print('Agent starting...')
        self.add_behaviour(self.MyBehav('test behaviour'))
        self.add_behaviour(self.OtherBehav('test2 behaviour'))


if __name__ == "__main__":
    dummy = DummyAgent(None, 'dummy@test.com')
    ams = AMS('localhost', 8080)
    dummy.register_ams(ams)
    ams.execute_agent(dummy.aid, ['test2 behaviour', 'test behaviour'])
    # dummy.run_behaviour('test behaviour')