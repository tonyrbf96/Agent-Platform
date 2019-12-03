import threading

class Behaviour:
    def __init__(self, name):
        self.lock = threading.Lock()
        self.lock.locked()
        self.name = name
        self._stop = threading.Event()
        self._end = threading.Event()

    def stop(self): 
        "Stops the behavior of the agent"
        self._stop.set()
        if not self.lock.locked():
            self.lock.acquire()

    @property
    def stopped(self):
        return self._stop.is_set()

    def end(self):
        "Ends the behavior of the agent"
        self._end.set()

    @property
    def ended(self):
        return self._end.is_set()


    def restart(self):
        "Allows the behaviour to be explicitly restarted"
        if not self._stop.is_set():
            return
        self._stop.clear()
        if self.lock.locked():
            self.lock.release()

    def on_start(self):
        "Function called before the behavior is started"
        pass

    def run(self, *args):
        "Starts the excecution of the agent"
        pass

    def done(self) -> bool:
        """Returns True if the behaviour has finished
        else returns False"""
        pass


def run_cyclic(func):
    def wrapper(self, *args):
        while True:
            if self.ended:
                return
            if self.stopped:
                self.lock.acquire()
            func(self, *args)
    return wrapper