#     nttv.space.AppPages     #
################################
#       by Porko c.(2025)      #
#---------------------------->importing data loaders
from CORE.Loaders.CoreLoader import *
from CORE.Loaders.LibsLoader import *
from CORE.Functions.Main.App import *
from CORE.Functions.Main.Router import ROUTES, METHODS

#----------------------------> Flask pages
def load():
    @app.before_request
    def check_ban_status():
        if 'user_id' in session:
            users = Console.load_users()
            user = users.get(session['user_id'])
            if user and "ban" in user.get('badges', []):
                if request.endpoint not in ('ban', 'favicon'):
                    return redirect(url_for('ban'))

    @app.template_filter('datetimeformat')
    def datetimeformat(value):
        return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))

    for route, handler in ROUTES.items():
        methods = METHODS.get(route, ['GET'])
        app.add_url_rule(route, view_func=handler, methods=methods)