class AMSAgentDescription:
    def __init__(self, aid, state):
        self.aid = aid
        self.current_state = state

    def change_to_state(self, state):
        self.current_state = state

class DFAgentDescription:
    def __init__(self, aid, services):
        self.aid = aid
        self.services = services

class ServiceDescription:
    "Describes the services that an agent provides"
    # Segun JADE incluye:
    # El tipo de servicio (e.g. "Weather forecast")
    # El nombre (e.g. "Mateo-1")
    # Los lenguajes, las antologías, y los protocolos de interacción
    # que se deben conocer para explotar el servicio
    # Una colección de propiedades de servicios especificadas en 
    # forma de pares clave-valor
    def __init__(self, name, type_):
        self.name = name
        self.type = type_