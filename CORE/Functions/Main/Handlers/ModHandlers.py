from CORE.Loaders.CoreLoader import *
from CORE.Loaders.LibsLoader import *
from CORE.Functions.Main.App import *

def mod_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    users = Console.load_users()
    user = users.get(user_id)

    if "mod" not in user.get('badges', []):
        return "Access denied", 403

    message = ""

    if request.method == 'POST':
        action = request.form.get('action')
        target_uid = request.form.get('uid')
        badge_name = request.form.get('badge')

        if action == 'assign_badge':
            Console.assign_badge_to_user(target_uid, badge_name)
            message = f"Badge '{badge_name}' assigned to user with UID {target_uid}."
        elif action == 'delete_user':
            Console.delete_user_account(target_uid)
            message = f"User with UID {target_uid} deleted."

    reports = Console.load_reports()

    return render_template('mod_page.html',
                           users=users,
                           badges=DataStrStatic.BADGES,
                           reports=reports,
                           message=message)