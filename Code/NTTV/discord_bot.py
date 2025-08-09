import discord
import asyncio
import json
import os
#import DB.str_db as db
TOKEN = 0
CONFIG_FILE = "db/shared_config.json"

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

default_config = {
    "announcement_channel_id": None
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return default_config
    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

@bot.event
async def on_ready():
    print(f"[DISCORD] Logged in as {bot.user}")

@bot.event
async def on_message(message):
    if not message.content.startswith("!setchannel"):
        return
    if not message.author.guild_permissions.administrator:
        await message.channel.send("⛔ Лише адміністратор може встановити канал.")
        return

    config = load_config()
    config['announcement_channel_id'] = message.channel.id
    save_config(config)
    await message.channel.send("✅ Канал для стрім-сповіщень встановлено.")

async def announce_stream(forum_name, author_nick, forum_url, stream_url):
    await bot.wait_until_ready()

    config = load_config()
    channel_id = config.get("announcement_channel_id")
    if not channel_id:
        print("[DISCORD] ❌ Канал для повідомлень не встановлено.")
        return

    # Надійний пошук каналу
    channel = None
    for guild in bot.guilds:
        channel = discord.utils.get(guild.text_channels, id=channel_id)
        if channel:
            break

    if not channel:
        print("[DISCORD] ❌ Канал не знайдено.")
        return

    embed = discord.Embed(
        title="🔴 Стрім розпочато!",
        description=f"**Користувач:** {author_nick}\n"
                    f"**Тема:** {forum_name}\n"
                    f"[🔗 Перейти до теми]({forum_url})",
        color=discord.Color.red()
    )

    await channel.send(embed=embed)


def run_discord_bot():
    try:
        bot.run(TOKEN)
    except Exception as e:
        print("[DISCORD] ❌ Error:", e)
