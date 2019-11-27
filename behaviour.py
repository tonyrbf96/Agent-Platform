class Behaviour:
    def __init__(self, name):
        self.name = name

    def on_start(self, *args):
        "This method runs when the behavior starts"
        pass

    def on_end(self, *args):
        "This method runs when the behavior stops"
        pass

    def block(self): 
        """Blocks the behaviour until some event happens 
        (typically, until a message arrives)"""
        pass

    def restart(self):
        "Allows the behaviour to be explicitly restarted"
        pass

    def run(self, *args):
        "Starts the excection of the agent"
        pass

    def done(self) -> bool:
        """Returns True if the behaviour has finished
        else returns False"""
        pass