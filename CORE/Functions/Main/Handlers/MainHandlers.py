from CORE.Loaders.CoreLoader import *
from CORE.Loaders.LibsLoader import *
from CORE.Functions.Main.App import *
import random

def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

def ban():
    return render_template('ban.html'), 403

def index():
    forums = Console.load_forums()
    all_topics = list(forums.values())
    top_topic = random.choice(all_topics) if all_topics else None
    return render_template("main.html", top_topic=top_topic)