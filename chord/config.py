import Pyro4

m = 7
M = (1 << m) - 1


Pyro4.config.SERIALIZER = 'pickle'
Pyro4.config.SERIALIZERS_ACCEPTED = {
    'serpent', 'json', 'marshal', 'pickle'}

STABILIZATION_TIME = 0.2
RETRY_TIME = STABILIZATION_TIME * 4
ASSURED_LIFE_TIME = RETRY_TIME * 4
