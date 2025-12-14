from CORE.Loaders.CoreLoader import *
from CORE.Loaders.LibsLoader import *
from CORE.Functions.Main.App import *

def profile():
    if 'user_id' in session:
        users = Console.load_users()
        user = users.get(session['user_id'])
        if user:
            user['badges'] = Console.get_ukrainian_badges(user)
            is_mod = "mod" in user.get('badges', [])
            return render_template("profile.html", user=user, is_mod=is_mod)
    return redirect(url_for('register'))

def view_user_profile(uid):
    users = Console.load_users()
    forums = Console.load_forums()

    user = users.get(uid)
    if not user:
        return "Користувача не знайдено", 404

    subscribed_forum_ids = user.get('subs', [])
    subscribed_forums = {
        fid: forums[fid]
        for fid in subscribed_forum_ids
        if fid in forums
    }

    translated_badges = Console.get_ukrainian_badges(user)

    return render_template(
        'user_profile.html',
        user=user,
        badges=translated_badges,
        subscribed_forums=subscribed_forums
    )

def profile_subs():
    if 'user_id' in session:
        users = Console.load_users()
        forums = Console.load_forums()
        user = users.get(session['user_id'])

        if user:
            subscribed_forum_ids = user.get('subs', [])
            subs = {fid: forums[fid] for fid in subscribed_forum_ids if fid in forums}
            
            from CORE.Functions.Main.Handlers.ForumHandlers import get_subscriber_count
            
            return render_template(
                "profile_subs.html",
                user=user,
                users=users,
                subs=subs,
                show_menu=None,
                get_subscriber_count=get_subscriber_count
            )

    return redirect(url_for('register'))

def update_user():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    users = Console.load_users()
    user = users.get(session['user_id'])

    if not user:
        return "User not found", 404
        
    bio = request.form.get('bio', '').strip()
    d_gmail = request.form.get('d_gmail', '').strip()

    if bio is not None:
        user['bio'] = bio

    if d_gmail is not None:
        user['d_gmail'] = d_gmail

    Console.save_users(users)
    return redirect(url_for('profile'))