#   nttv.space.App.ServerThreading     #
########################################
#            by Porko c.(2025)         #
#---------------------------->importing data loaders
from CORE.Loaders.CoreLoader import *
from CORE.Loaders.LibsLoader import *
from CORE.Functions.Main.App import *

#--------------------------->core actions
core = str(DataStrStatic.core)
class ServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.daemon = True


    def run(self):
        print(core + " Server starting...")
        serve(self.app, host=DataTechStatic.ip, port=DataTechStatic.port)
        print(core + " Server started")

def start(app):
    ST = ServerThread(app)

    print(core + " Starting NTTV server…")
    if ST and ST.is_alive():
        print(core + " NTTV server is already running.")
        return

    try:
        ST.start()
        print(core + " Server started successfully.")
    except Exception as e:
        print(core + f" Error starting server: {e}")