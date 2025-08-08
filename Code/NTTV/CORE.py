from flask import Flask, render_template, request, redirect, url_for, session , send_from_directory
import time
from flask_socketio import SocketIO
import requests
import threading
import os
import sys
from colorama import init , Fore
from werkzeug.security import generate_password_hash, check_password_hash
from waitress import serve
import uuid
import json
from Console import *
import random
import asyncio


init(autoreset=True)

# ------------->bools
# >app main
app = Flask(__name__)
app.secret_key =  os.environ.get("SECRET_KEY", os.urandom(24))

ip = "0.0.0.0"
port = "9999"

socketio = SocketIO(app)

server_thread = None
http_server = None

core = "[CORE]"
#------------->start up
@app.before_request
def check_ban_status():
    if 'user_id' in session:
        users = load_users()
        user = users.get(session['user_id'])
        if user and "ban" in user.get('badges', []):
            if request.endpoint not in ('ban', 'favicon'):
                return redirect(url_for('ban'))

@app.route('/ban')
def ban():
    return render_template('ban.html'), 403

# >іконка
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )


@app.template_filter('datetimeformat')
def datetimeformat(value):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(value))


# ------------->pages
@app.route('/')
def index():
    forums = load_forums()

    all_topics = list(forums.values())
    top_topic = random.choice(all_topics) if all_topics else None

    return render_template("main.html", top_topic=top_topic)

# >forum
def get_subscriber_count(forum_id):
    users = load_users()
    count = sum(1 for user in users.values() if forum_id in user['subs'])
    return count

@app.route('/forums', methods=['GET', 'POST'])
def forums():
    if request.method == 'POST':
        forum_name = request.form['forum_name']
        forum_description = request.form['forum_description']

        if 'user_id' not in session:
            return redirect(url_for('login'))

        user_id = session['user_id']
        forums = load_forums()

        forum_id = str(uuid.uuid4())

        forums[forum_id] = {
            'id': forum_id,
            'name': forum_name,
            'description': forum_description,
            'author_id': user_id,
            'reputation': 0,
            'votes': [],
            'subscribers': [],
            'state': None,
            'is_live': False,
            'youtube_stream_url': '',
            'kick_stream_url': '',
        }

        save_forums(forums)
        return redirect(url_for('forums'))

    forums = load_forums()
    users = load_users()

    sorted_forums = sorted(forums.items(), key=lambda x: x[1]['reputation'], reverse=True)

    return render_template(
        "forums.html",
        forums=sorted_forums,
        users=users,
        get_subscriber_count=get_subscriber_count,
        show_menu=None
    )

@app.route('/forums/vote/<forum_id>', methods=['POST'])
def vote_forum(forum_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    vote_type = request.form.get('vote')

    forums = load_forums()
    if forum_id not in forums:
        return "Forum not found", 404

    forum = forums[forum_id]
    votes = forum['votes']

    if vote_type == 'up':
        if user_id not in votes:
            votes.append(user_id)
            forum['reputation'] += 1
    elif vote_type == 'down':
        if user_id not in votes:
            votes.append(user_id)
            forum['reputation'] -= 1
    elif vote_type == 'cancel':
        if user_id in votes:
            votes.remove(user_id)
            if forum['reputation'] > 0:
                forum['reputation'] -= 1
            else:
                forum['reputation'] += 1

    forum['votes'] = votes
    save_forums(forums)

    return redirect(url_for('forums', show_menu=forum_id))


@app.route('/forums/subscribe/<forum_id>', methods=['POST'])
def subscribe_forum(forum_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    users = load_users()
    forums = load_forums()

    if forum_id not in forums:
        return "Forum not found", 404

    forum = forums[forum_id]
    user = users.get(user_id)

    if user is None:
        return "User not found", 404

    if forum_id not in user.get('subs', []):
        user.setdefault('subs', []).append(forum_id)

    if user_id not in forum.get('subscribers', []):
        forum.setdefault('subscribers', []).append(user_id)

    save_users(users)
    save_forums(forums)

    return redirect(url_for('forums'))


@app.route('/forums/unsubscribe/<forum_id>', methods=['POST'])
def unsubscribe_forum(forum_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    users = load_users()
    forums = load_forums()

    if forum_id not in forums:
        return "Forum not found", 404

    forum = forums[forum_id]
    user = users.get(user_id)

    if user is None:
        return "User not found", 404


    if forum_id in user.get('subs', []):
        user['subs'].remove(forum_id)


    if user_id in forum.get('subscribers', []):
        forum['subscribers'].remove(user_id)

    # Збереження змін
    save_users(users)
    save_forums(forums)

    return redirect(url_for('forums'))




@app.route('/forums/delete/<forum_id>', methods=['POST'])
def delete_forum(forum_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    forums = load_forums()

    if forum_id not in forums:
        return "Forum not found", 404

    forum = forums[forum_id]
    user = load_users().get(user_id)


    if forum['author_id'] != user_id and "mod" not in user.get('badges', []):
        return "You are not the author of this forum or a moderator", 403

    del forums[forum_id]
    save_forums(forums)

    return redirect(url_for('forums'))

# >profile
@app.route('/profile')
def profile():
    if 'user_id' in session:
        users = load_users()
        user = users.get(session['user_id'])
        if user:
            user['badges'] = get_ukrainian_badges(user)
            is_mod = "mod" in user.get('badges', [])
            return render_template("profile.html", user=user , is_mod= is_mod)
    return redirect(url_for('register'))

@app.route('/user/<uid>')
def view_user_profile(uid):
    users = load_users()
    forums = load_forums()

    user = users.get(uid)
    if not user:
        return "Користувача не знайдено", 404

    subscribed_forum_ids = user.get('subs', [])
    subscribed_forums = {
        fid: forums[fid]
        for fid in subscribed_forum_ids
        if fid in forums
    }

    # Перекладаємо бейджі тут
    translated_badges = get_ukrainian_badges(user)

    return render_template(
        'user_profile.html',
        user=user,
        badges=translated_badges,
        subscribed_forums=subscribed_forums
    )


@app.route('/profile_subs')
def profile_subs():
    if 'user_id' in session:
        users = load_users()
        forums = load_forums()
        user = users.get(session['user_id'])

        if user:
            subscribed_forum_ids = user.get('subs', [])
            subs = {fid: forums[fid] for fid in subscribed_forum_ids if fid in forums}
            return render_template(
                "profile_subs.html",
                user=user,
                users=users,
                subs=subs,
                show_menu=None,
                get_subscriber_count=get_subscriber_count
            )

    return redirect(url_for('register'))


# >API Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return "Missing fields", 400

        users = load_users()
        uid = str(uuid.uuid4())
        if data['email'] in [user['email'] for user in users.values()]:
            return "Email already in use", 400

        user_id = str(uuid.uuid4())
        hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

        users[user_id] = {
            'uid': uid,
            'username': data['username'],
            'email': data['email'],
            'password_hash': hashed_password,
            'badges': [],
            'subs': [],
            'bio': '',
            'd_gmail': ''
        }



        # Assign the "new_user" badge upon registration
        assign_badge(users[user_id], "new_user")
        print_user_info("new user (writed to data) " , uid)
        save_users(users)
        session['user_id'] = user_id
        return redirect(url_for('index'))

    return render_template('register.html')

@app.route('/update_user', methods=['POST'])
def update_user():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    users = load_users()
    user = users.get(session['user_id'])

    if not user:
        return "User not found", 404
    bio = request.form.get('bio', '').strip()
    d_gmail = request.form.get('d_gmail', '').strip()

    if bio is not None:
        user['bio'] = bio

    if d_gmail is not None:
        user['d_gmail'] = d_gmail

    save_users(users)
    return redirect(url_for('profile'))

# >API enter
@app.route('/login', methods=['GET', 'POST'])
def login():
    user = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        users = load_users()

        # Search for the user by email
        for user_id, user_data in users.items():
            if user_data['email'] == email:
                user = user_data
                break

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user_id

            user['login_count'] = user.get('login_count', 0) + 1
            if user['login_count'] > 10:
                assign_badge(user, "frequent_user")

            save_users(users)
            print_user_info("user logined" , user_id)
            return redirect(url_for('profile'))
        else:
            print_warning("somebody trying to login (fail trap)")
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')
# ------------->moderating
REPORTS_FILE = 'reports.json'


def load_reports():
    if os.path.exists(REPORTS_FILE):
        with open(REPORTS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_reports(reports):
    with open(REPORTS_FILE, 'w') as f:
        json.dump(reports, f, indent=4)


@app.route('/forums/moderate/<forum_id>', methods=['GET', 'POST'])
def moderate_forum(forum_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    forums = load_forums()
    users = load_users()

    if forum_id not in forums:
        return "Forum not found", 404

    forum = forums[forum_id]
    user = users.get(user_id)

    if forum['author_id'] != user_id and "mod" not in user.get('badges', []):
        return "Access denied", 403

    forum.setdefault('banned_users', [])
    forum.setdefault('is_live', False)
    forum.setdefault('kick_nickname', None)
    forum.setdefault('youtube_stream_url', '')
    forum.setdefault('kick_stream_url', '')


    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'edit':
            forum['name'] = request.form.get('forum_name') or forum['name']
            forum['description'] = request.form.get('forum_description') or forum['description']
            save_forums(forums)
            return redirect(url_for('moderate_forum', forum_id=forum_id))

        elif action == 'delete':
            del forums[forum_id]
            save_forums(forums)
            return redirect(url_for('forums'))

        elif action == 'report':
            report_uid = request.form.get('report_uid')
            reason = request.form.get('reason', '')
            if report_uid:
                reports = load_reports()
                report_id = str(uuid.uuid4())
                reports[report_id] = {
                    'forum_id': forum_id,
                    'reported_uid': report_uid,
                    'reporter_uid': user_id,
                    'reason': reason,
                    'timestamp': time.time()
                }
                save_reports(reports)
            return redirect(url_for('moderate_forum', forum_id=forum_id))
        elif action == 'start_stream':
            forum['is_live'] = True
            save_forums(forums)

            author_name = users.get(forum['author_id'], {}).get('username', 'Невідомий')
            forum_url = f"http://nttv.space/forums/view/{forum_id}"
            stream_url = forum.get('youtube_stream_url') or forum.get('kick_stream_url') or forum_url

            def run_announce():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.close()

            threading.Thread(target=run_announce, daemon=True).start()

            return redirect(url_for('moderate_forum', forum_id=forum_id))



        elif action == 'stop_stream':
            forum['is_live'] = False
            save_forums(forums)
            return redirect(url_for('moderate_forum', forum_id=forum_id))

        elif action == 'set_kick_nickname':
            kick_nickname = request.form.get('kick_nickname')
            if kick_nickname:
                forum['kick_nickname'] = kick_nickname
                save_forums(forums)
            return redirect(url_for('moderate_forum', forum_id=forum_id))
        elif action == 'update_stream_links':
            youtube_url = request.form.get('youtube_stream_url', '').strip()
            kick_url = request.form.get('kick_stream_url', '').strip()

            forum['youtube_stream_url'] = youtube_url
            forum['kick_stream_url'] = kick_url
            save_forums(forums)
            return redirect(url_for('moderate_forum', forum_id=forum_id))



    subscriber_count = len(forum.get('subscribers', []))
    banned_users_info = [users.get(uid, {'username': 'Unknown'}) for uid in forum['banned_users']]

    return render_template('moderate_forum.html',
                           forum=forum,
                           subscriber_count=subscriber_count,
                           banned_users=banned_users_info,
                           forum_id=forum_id)

@app.route('/forums/view/<forum_id>', methods=['GET', 'POST'])
def view_forum(forum_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    forums = load_forums()
    users = load_users()

    if forum_id not in forums:
        return "Форум не знайдено", 404

    forum = forums[forum_id]
    user = users.get(session['user_id'])
    user_id = session['user_id']

    if request.method == 'POST':
        if request.form.get('action') == 'delete_message':
            index = int(request.form.get('message_index'))
            if user_id == forum['author_id'] or 'mod' in user.get('badges', []):
                if 0 <= index < len(forum.get('messages', [])):
                    del forum['messages'][index]
                    save_forums(forums)
            return redirect(url_for('view_forum', forum_id=forum_id))

        message_text = request.form.get('message')
        if message_text:
            message = {
                'author_id': user_id,
                'text': message_text,
                'timestamp': time.time()
            }
            forum.setdefault('messages', []).append(message)
            save_forums(forums)
            return redirect(url_for('view_forum', forum_id=forum_id))

    messages = [
        {
            'username': users.get(msg['author_id'], {}).get('username', 'Невідомий'),
            'author_id': msg["author_id"],
            'text': msg['text'],
            'timestamp': time.strftime('%H:%M %Y-%m-%d', time.localtime(msg['timestamp']))
        }
        for msg in forum.get('messages', [])
    ]

    return render_template('view_forum.html', forum=forum, messages=messages, users=users)

@app.route('/forums/<forum_id>/chat', methods=['GET', 'POST'])
def forum_chat(forum_id):
    forums = load_forums()
    users = load_users()

    if forum_id not in forums:
        return "Форум не знайдено", 404

    forum = forums[forum_id]
    forum['id'] = forum_id  # Додаємо для шаблону

    if request.method == 'POST':
        message_text = request.form.get('message')
        if message_text:
            forum.setdefault('messages', []).append({
                'author_id': session['user_id'],
                'text': message_text,
                'timestamp': time.strftime('%H:%M %Y-%m-%d', time.localtime())
            })
            save_forums(forums)
            return redirect(url_for('forum_chat', forum_id=forum_id))

    messages = [
        {
            'username': users.get(msg['author_id'], {}).get('username', 'Невідомий'),
            'text': msg['text'],
            'timestamp': msg['timestamp']
        }
        for msg in forum.get('messages', [])
    ]

    return render_template('chat.html', forum=forum, messages=messages)


@app.route('/forums/<forum_id>/get_messages')
def get_forum_messages(forum_id):
    forums = load_forums()
    users = load_users()

    if forum_id not in forums:
        return "Форум не знайдено", 404

    forum = forums[forum_id]

    messages = [
    {
        'username': users.get(msg['author_id'], {}).get('username', 'Невідомий'),
        'text': msg['text'],
        'timestamp': msg['timestamp']
    }
    for msg in forum.get('messages', [])[::-1]
    ]

    return ''.join(
        f"<li class='message'><h4>{msg['username']}</h4><p>{msg['text']}</p><small>{msg['timestamp']}</small></li>"
        for msg in messages
    )

#-------------> administrating

@app.route('/mod_page', methods=['GET', 'POST'])
def mod_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    users = load_users()
    user = users.get(user_id)

    if "mod" not in user.get('badges', []):
        return "Access denied", 403

    message = ""

    if request.method == 'POST':
        action = request.form.get('action')
        target_uid = request.form.get('uid')
        badge_name = request.form.get('badge')

        if action == 'assign_badge':
            assign_badge_to_user(target_uid, badge_name)
            message = f"Badge '{badge_name}' assigned to user with UID {target_uid}."
        elif action == 'delete_user':
            delete_user_account(target_uid)
            message = f"User with UID {target_uid} deleted."

    reports = load_reports()

    return render_template('mod_page.html',
                           users=users,
                           badges=BADGES,
                           reports=reports,
                           message=message)


# ------------->core actions

class ServerThread(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.daemon = True

    def run(self):
        print(core + " Server starting...")
        serve(self.app, host=ip, port=port)
        print(core + " Server started")

    def shutdown(self):
        print(core + " Server shutting down...")


def start():
    app.run(debug=True)

# ------------->console

# >run
if __name__ == "__main__":
    start()
