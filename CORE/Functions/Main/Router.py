from CORE.Functions.Main.Handlers.MainHandlers import *
from CORE.Functions.Main.Handlers.ForumHandlers import *
from CORE.Functions.Main.Handlers.ProfileHandlers import *
from CORE.Functions.Main.Handlers.AuthHandlers import *
from CORE.Functions.Main.Handlers.ModHandlers import *

ROUTES = {
    # main page
    '/': index,
    '/ban': ban,
    '/favicon.ico': favicon,
    
    # forums
    '/forums': forums,
    '/forums/vote/<forum_id>': vote_forum,
    '/forums/subscribe/<forum_id>': subscribe_forum,
    '/forums/unsubscribe/<forum_id>': unsubscribe_forum,
    '/forums/delete/<forum_id>': delete_forum,
    '/forums/moderate/<forum_id>': moderate_forum,
    '/forums/view/<forum_id>': view_forum,
    '/forums/<forum_id>/chat': forum_chat,
    '/forums/<forum_id>/get_messages': get_forum_messages,
    
    # profile
    '/profile': profile,
    '/user/<uid>': view_user_profile,
    '/profile_subs': profile_subs,
    '/update_user': update_user,
    
    # register
    '/register': register,
    '/login': login,
    
    # mod
    '/mod_page': mod_page,
}

METHODS = {
    '/': ['GET'],
    '/ban': ['GET'],
    '/favicon.ico': ['GET'],
    '/forums': ['GET', 'POST'],
    '/forums/vote/<forum_id>': ['POST'],
    '/forums/subscribe/<forum_id>': ['POST'],
    '/forums/unsubscribe/<forum_id>': ['POST'],
    '/forums/delete/<forum_id>': ['POST'],
    '/forums/moderate/<forum_id>': ['GET', 'POST'],
    '/forums/view/<forum_id>': ['GET', 'POST'],
    '/forums/<forum_id>/chat': ['GET', 'POST'],
    '/forums/<forum_id>/get_messages': ['GET'],
    '/profile': ['GET'],
    '/user/<uid>': ['GET'],
    '/profile_subs': ['GET'],
    '/update_user': ['POST'],
    '/register': ['GET', 'POST'],
    '/login': ['GET', 'POST'],
    '/mod_page': ['GET', 'POST'],
}