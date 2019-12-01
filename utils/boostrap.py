class Boostrap:
    def __init__(self):
        self.table = {}


    def __iter__(self):
        for k, v in self.table.items():
            yield k, v

    def register(self, name, uri):
        "Registers a node in the boostrap"
        print('---------------------------------------------------')
        print(f'Registrando name: {name}, uri: {uri}')
        if name in self.table:
            print(f'No se pudo registrar name: {name}, uri: {uri}')
            return False

        # r_uri = None
        # if self.table:
        #     r_uri = self.get_node()
        self.table[name] = uri
        print(f'Registrado con éxito: {name}, uri: {uri}')
        return True


    def is_registered(self, name, uri):
        "Checks if a node is registered in the boostrap"
        try:
            register = self.table[name]
            result = register == uri
        except KeyError:
            result = False
        print(f'Consultando si registrado: {name} {uri} Result: {result}')
        return result

    def unregister(self, name):
        print('---------------------------------------------------')
        print('Eliminando id:', name)
        try:
            del self.table[name]
            print('Eliminado con éxito.')
        except:
            print('Nombre no registrado.')
            return

    def get_node(self):
        print('---------------------------------------------------')
        print('Obteniendo nodo...')
        node = self.table.popitem()
        self.table[node[0]] = node[1]
        print('Devolviendo:', node[1])
        return node[1]
    