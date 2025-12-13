#     nttv.space.App.startUP   #
################################
#       by Porko c.(2025)      #
#---------------------------->importing data to load
import CORE.Functions.Main.App as A
import CORE.Functions.Main.AppPages as AP
import CORE.Functions.Main.ServerThreading as ST
import CORE.Functions.Console.Console as C
#---------------------------->initing everything
if __name__ == "__main__":
    A.startup()
    AP.load()
    ST.start(A.app)
    C.handle_console()


