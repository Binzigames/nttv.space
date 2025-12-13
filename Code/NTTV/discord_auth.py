from flask import Blueprint, request, jsonify
import requests
from dotenv import load_dotenv
import os

load_dotenv()  # ← завантажує .env

discord_auth = Blueprint("discord_auth", __name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

TOKEN_URL ="https://discord.com/api/oauth2/token"
USER_URL = "https://discord.com/api/users/@me"
REDIRECT_URI = "http://192.168.0.109:9999/callback"


@discord_auth.route("/callback")
def callback():
    code = request.args.get("code")

    if not code:
        return jsonify({"error": "No code provided"}), 400

    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "scope": "identify email"
    }

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    token_res = requests.post(TOKEN_URL, data=data, headers=headers)
    token_json = token_res.json()

    access_token = token_json.get("access_token")

    if not access_token:
        return jsonify({"error": "Failed to get access token", "details": token_json}), 400

    user_res = requests.get(
        USER_URL,
        headers={"Authorization": f"Bearer {access_token}"}
    )

    user = user_res.json()
    print(user)

    return jsonify({
        "id": user["id"],
        "username": user["username"],
        "discriminator": user["discriminator"],
        "email": user.get("email"),
        "avatar": user["avatar"]
    })
