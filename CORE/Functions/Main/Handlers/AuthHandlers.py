from CORE.Loaders.CoreLoader import *
from CORE.Loaders.LibsLoader import *
from CORE.Functions.Main.App import *

def register():
    if request.method == 'POST':
        data = request.form
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return "Missing fields", 400

        users = Console.load_users()
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

        Console.assign_badge(users[user_id], "new_user")
        Console.print_user_info("new user (writed to data) ", uid)
        Console.save_users(users)
        session['user_id'] = user_id
        return redirect(url_for('index'))

    return render_template('register.html')

def login():
    user = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        users = Console.load_users()

        for user_id, user_data in users.items():
            if user_data['email'] == email:
                user = user_data
                break

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user_id

            user['login_count'] = user.get('login_count', 0) + 1
            if user['login_count'] > 10:
                Console.assign_badge(user, "frequent_user")

            Console.save_users(users)
            Console.print_user_info("user logined", user_id)
            return redirect(url_for('profile'))
        else:
            Console.print_warning("somebody trying to login (fail trap)")
            return render_template('login.html', error="Invalid credentials")

    return render_template('login.html')