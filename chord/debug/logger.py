import logging
import logging.config
import yaml
import os
# path = os.path.dirname(os.path.abspath(__file__))


#formatter
fformatter = logging.Formatter('%(asctime)s %(levelname)s %(name)s: %(message)s',datefmt='%M:%S') 
cformatter =  logging.Formatter('%(levelname)s : %(message)s') 

#handlers
consoleHandler = logging.StreamHandler()
fileHandler = logging.FileHandler(filename='./logs/debug.log')
consoleHandler.formatter = cformatter
fileHandler.formatter = fformatter

logger = None

def init_logger(name:str,level:int):
    global logger
    print(name)
    logger = logging.getLogger(name)
    logger.addHandler(consoleHandler)
    logger.addHandler(fileHandler)
    logger.setLevel(level)
    
    
DEBUG = logging.DEBUG
INFO = logging.INFO

def info(msg:str):
    global logger
    logger.info(msg)
    
def debug(msg:str):
    global logger
    logger.debug(msg)
    
def error(msg:str):
    logger.error(msg)
    
    
def exception(msg):
     logger.exception(msg)