from CORE.Loaders.CoreLoader import *
from CORE.Loaders.LibsLoader import *
from CORE.Functions.Main.App import *

def get_subscriber_count(forum_id):
    users = Console.load_users()
    count = sum(1 for user in users.values() if forum_id in user['subs'])
    return count

def forums():
    if request.method == 'POST':
        forum_name = request.form['forum_name']
        forum_description = request.form['forum_description']

        if 'user_id' not in session:
            return redirect(url_for('login'))

        user_id = session['user_id']
        forums = Console.load_forums()
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

        Console.save_forums(forums)
        return redirect(url_for('forums'))

    forums = Console.load_forums()
    users = Console.load_users()
    sorted_forums = sorted(forums.items(), key=lambda x: x[1]['reputation'], reverse=True)

    return render_template(
        "forums.html",
        forums=sorted_forums,
        users=users,
        get_subscriber_count=get_subscriber_count,
        show_menu=None
    )

def vote_forum(forum_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    vote_type = request.form.get('vote')
    forums = Console.load_forums()
    
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
    Console.save_forums(forums)
    return redirect(url_for('forums', show_menu=forum_id))

def subscribe_forum(forum_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    users = Console.load_users()
    forums = Console.load_forums()

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

    Console.save_users(users)
    Console.save_forums(forums)
    return redirect(url_for('forums'))

def unsubscribe_forum(forum_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    users = Console.load_users()
    forums = Console.load_forums()

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

    Console.save_users(users)
    Console.save_forums(forums)
    return redirect(url_for('forums'))

def delete_forum(forum_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    forums = Console.load_forums()

    if forum_id not in forums:
        return "Forum not found", 404

    forum = forums[forum_id]
    user = Console.load_users().get(user_id)

    if forum['author_id'] != user_id and "mod" not in user.get('badges', []):
        return "You are not the author of this forum or a moderator", 403

    del forums[forum_id]
    Console.save_forums(forums)
    return redirect(url_for('forums'))

def moderate_forum(forum_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    forums = Console.load_forums()
    users = Console.load_users()

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
            Console.save_forums(forums)
            return redirect(url_for('moderate_forum', forum_id=forum_id))

        elif action == 'delete':
            del forums[forum_id]
            Console.save_forums(forums)
            return redirect(url_for('forums'))

        elif action == 'report':
            report_uid = request.form.get('report_uid')
            reason = request.form.get('reason', '')
            if report_uid:
                reports = Console.load_reports()
                report_id = str(uuid.uuid4())
                reports[report_id] = {
                    'forum_id': forum_id,
                    'reported_uid': report_uid,
                    'reporter_uid': user_id,
                    'reason': reason,
                    'timestamp': time.time()
                }
                Console.save_reports(reports)
            return redirect(url_for('moderate_forum', forum_id=forum_id))

        elif action == 'start_stream':
            forum['is_live'] = True
            Console.save_forums(forums)
            return redirect(url_for('moderate_forum', forum_id=forum_id))

        elif action == 'stop_stream':
            forum['is_live'] = False
            Console.save_forums(forums)
            return redirect(url_for('moderate_forum', forum_id=forum_id))

        elif action == 'set_kick_nickname':
            kick_nickname = request.form.get('kick_nickname')
            if kick_nickname:
                forum['kick_nickname'] = kick_nickname
                Console.save_forums(forums)
            return redirect(url_for('moderate_forum', forum_id=forum_id))

        elif action == 'update_stream_links':
            youtube_url = request.form.get('youtube_stream_url', '').strip()
            kick_url = request.form.get('kick_stream_url', '').strip()
            forum['youtube_stream_url'] = youtube_url
            forum['kick_stream_url'] = kick_url
            Console.save_forums(forums)
            return redirect(url_for('moderate_forum', forum_id=forum_id))

    subscriber_count = len(forum.get('subscribers', []))
    banned_users_info = [users.get(uid, {'username': 'Unknown'}) for uid in forum['banned_users']]

    return render_template('moderate_forum.html',
                           forum=forum,
                           subscriber_count=subscriber_count,
                           banned_users=banned_users_info,
                           forum_id=forum_id)

def view_forum(forum_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    forums = Console.load_forums()
    users = Console.load_users()

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
                    Console.save_forums(forums)
            return redirect(url_for('view_forum', forum_id=forum_id))

        message_text = request.form.get('message')
        if message_text:
            message = {
                'author_id': user_id,
                'text': message_text,
                'timestamp': time.time()
            }
            forum.setdefault('messages', []).append(message)
            Console.save_forums(forums)
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

def forum_chat(forum_id):
    forums = Console.load_forums()
    users = Console.load_users()

    if forum_id not in forums:
        return "Форум не знайдено", 404

    forum = forums[forum_id]
    forum['id'] = forum_id

    if request.method == 'POST':
        message_text = request.form.get('message')
        if message_text:
            forum.setdefault('messages', []).append({
                'author_id': session['user_id'],
                'text': message_text,
                'timestamp': time.strftime('%H:%M %Y-%m-%d', time.localtime())
            })
            Console.save_forums(forums)
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

def get_forum_messages(forum_id):
    forums = Console.load_forums()
    users = Console.load_users()

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