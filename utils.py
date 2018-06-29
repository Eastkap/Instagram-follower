from discord_hooks import Webhook
import requests
from multiprocessing import Process, Queue, Lock
from colorama import init, Fore
from datetime import datetime
import time
import requests

def get_full_date_logging():
    return str(datetime.now())[:][:-3].replace(' ','_')

def get_date_logging():
    return str(datetime.now())[11:][:-3]

class Logger: 
    def __init__(self,webhookurl=None, filename = None): 
        init(autoreset=True)
        self.lock = Lock()
        if webhookurl:
            self.webhookurl = webhookurl
        #if no  filename is included as a string, it assumes you don't want to create a log file
        if filename == None:
            self.logToTxt = False
        else:
            self.logToTxt = True
            self.filename = filename
            #self.file = open(filename, 'w+')

    def write2file(self,text):
        if self.webhookurl:
            msg = Webhook(self.webhookurl,msg=str(text))
            msg.post()
        with self.lock:
            with open(self.filename,'a') as file:
                file.write(text)


    def success(self, message):
        message = str(message)
        print(Fore.GREEN + "["+ get_date_logging()+"] " + message)
        if (self.logToTxt):
            self.write2file("["+ get_date_logging()+"] " + "SUCCESS: " + message + '\n')

    def warn(self, message):
        message = str(message)
        print(Fore.YELLOW + "["+ get_date_logging()+"] " + message)
        if (self.logToTxt):
            self.write2file("["+ get_date_logging()+"] " + "WARNING: " + message + '\n')

    def log(self, message):
        message = str(message)
        print(Fore.BLUE + "["+ get_date_logging()+"] " + message)
        if (self.logToTxt):
            self.write2file("["+ get_date_logging()+"] " + message + '\n')

    def error(self, message):
        message = str(message)
        print(Fore.RED + "["+ get_date_logging()+"] " + message)
        if (self.logToTxt):
            self.write2file("["+ get_date_logging()+"] " + "ERROR: " + message + '\n')

    def status(self, message):
        message = str(message)
        print(Fore.MAGENTA + "["+ get_date_logging()+"] " + message)
        if (self.logToTxt):
            self.write2file("["+ get_date_logging()+"] " + "STATUS: " + message + '\n')