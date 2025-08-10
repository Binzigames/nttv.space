#   nttv.space.console  #
#########################
#  by Porko c.(2025)    #
#-------------> importing
#python
import sys
import time
import json
import os
import socket

#other
from colorama import Fore
#-------------> databases
# database bools
#> file sys.
USERS_FILE = 'DB/users.json'
FORUMS_FILE = 'DB/forums.json'
REPORTS_FILE = 'DB/reports.json'

#> badges
BADGES = {
    "new_user": "Новачок",
    "early_bird": "Рання пташка",
    "frequent_user": "Частий користувач",
    "steamer": "стрімер",
    "mod": "Модератор платформи",
    "ban":"Бан",
    "verf":"Верифіковано"
}

#>stuff
Clog = False
port = "9998"

#-------------> databases defs
#> reports load
def load_reports():
    if os.path.exists(REPORTS_FILE):
        with open(REPORTS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_reports(reports):
    with open(REPORTS_FILE, 'w') as f:
        json.dump(reports, f, indent=4)

def print_server_ip():
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        print_success(f"Server IP address: {ip_address}:{port}")
    except Exception as e:
        print_error(f"Failed to get IP address: {e}")


# >data base load
def get_ukrainian_badges(user):
    return [BADGES.get(badge, badge) for badge in user.get('badges', [])]

def delete_user_account(uid):
    users = load_users()
    user = next((u for u in users.values() if u['uid'] == uid), None)
    if user:
        del users[uid]
        save_users(users)
        print_success(f"User with UID {uid} has been deleted successfully.")
    else:
        print_error(f"User with UID {uid} not found.")
#>users list
def load_users():
    if not os.path.exists(USERS_FILE):
        return {}

    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (json.JSONDecodeError, IOError) as e:
        print(f"[ERROR] load_users(): {e}")
        return {}

def save_users(users):
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=4)
    except IOError as e:
        print(f"[ERROR] save_users(): {e}")

#>forums list
def load_forums():
    if os.path.exists(FORUMS_FILE):
        with open(FORUMS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_forums(forums):
    with open(FORUMS_FILE, 'w') as f:
        json.dump(forums, f, indent=4)

# ------------->badge system
def assign_badge(user_data, badge):
    if badge not in user_data.get('badges', []):
        user_data['badges'] = user_data.get('badges', [])
        user_data['badges'].append(badge)

#> defs
def assign_badge_to_user(uid, badge_name):
    users = load_users()
    user = next((u for u in users.values() if u['uid'] == uid), None)
    if user:
        if badge_name in BADGES:
            assign_badge(user, badge_name)
            save_users(users)
            print(f"Badge '{BADGES[badge_name]}' has been assigned to user {user['username']} ({uid})")
        else:
            print(f"Invalid badge name: {badge_name}")
    else:
        print(f"User with UID {uid} not found.")
#-------------> console
def print_ascii_art():
    print(Fore.GREEN + "NTTV")
    print(Fore.GREEN + "developed by porko_dev")
    print_info("NTTV Server Starting...")

def print_info(message):
    print(Fore.CYAN + f"[INFO] {message}")

def print_error(message):
    print(Fore.RED + f"[ERROR] {message}")

def print_success(message):
    print(Fore.GREEN + f"[SUCCESS] {message}")

def print_warning(message):
    print(Fore.YELLOW + f"[WARNING] {message}")
def print_user_info(message , uid):
    print(Fore.LIGHTYELLOW_EX + f"[USER] {message} ({uid})")
# Спінер для візуального індикатора
def loading_spinner(message):
    spinner = ['|', '/', '-', '\\']
    for _ in range(30):  # Прокрутка спінера
        sys.stdout.write(f"\r{Fore.YELLOW}[INFO] {message} {spinner[_ % 4]}")
        sys.stdout.flush()
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * 50 + "\r")  # Очищаємо рядок

def handle_console():
    global debuger
    print_ascii_art()
    print_info("NTTV Debugger: Console is ready. Waiting for commands...")

    while True:
        I = input(Fore.MAGENTA + "> ").strip()

        if I == "debuger":
            debuger = not debuger
            print_success(f"Debug mode: {debuger}")
        elif I == "help":
            print_help()
        elif I == "exit":
            print_info("Exiting console...")
            sys.exit(1)

        elif I.startswith("assign_badge"):
            try:
                _, uid, badge_name = I.split()
                assign_badge_to_user(uid, badge_name)
                print_success(f"Badge '{badge_name}' has been assigned to user {uid}.")
            except ValueError:
                print_error("Invalid command format. Use: assign_badge <uid> <badge_name>")

        elif I.startswith("delete_user"):
            try:
                _, uid = I.split()
                delete_user_account(uid)
            except ValueError:
                print_error("Invalid command format. Use: delete_user <uid>")
        elif I == "Clog":
            global Clog
            Clog = not Clog
            print_info(f"Clog : {Clog}")
        elif I == "ip":
            print_server_ip()
        else:
            print_error("Unknown command. Type 'help' for a list of available commands.")


def print_help():
    print_info("help menu :")
    print_info("Available commands:         /       func.:        ")
    print_info("start                                - Start the server")
    print_info("debuger                              - turns on off debuger")
    print_info("assign_badge <uid> <badge_name>      - Assign a badge to a user")
    print_info("delete_user <uid>                    - delete user data")
    print_info("exit                                 - Exit the console")
    print_info("Clog                                 - shows some users action")
    print_info("ip                                   - Show server IP address")
