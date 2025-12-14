#       nttv.space.App       #
##############################
#       by Porko c.(2025)    #
#---------------------------->importing data loaders
from CORE.Loaders.CoreLoader import *
from CORE.Loaders.LibsLoader import *
#---------------------------->Flask app to use
init(autoreset=True)

app = Flask(
    __name__,
    template_folder="../../web/templates",
    static_folder="../../web/static",
)

#----------------------------> Flask application init
def startup():

    app.secret_key = os.environ.get("SECRET_KEY", os.urandom(24))
    app.permanent_session_lifetime = timedelta(hours=int(DataTechStatic.TimeToRelog))


##############################
#its just app init... lol