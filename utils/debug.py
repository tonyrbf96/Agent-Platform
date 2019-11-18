VERBOSE = True

class Debug:

    @staticmethod
    def log(msg:str,name:str=''):
        if VERBOSE:
            print(f'{name}{msg}')

    @staticmethod
    def log_error(error:str):
        if VERBOSE:
            print(f'Error: {error}') #TODO: implement red color in terminal
        pass
