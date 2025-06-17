import discord
from discord.ext import tasks, commands
import os
import json
from keep_alive import keep_alive
from datetime import time
import requests

TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

USER_IDS = {
    "Gaurav": os.environ['Gaurav'],   # Replace with Gaurav's actual ID
    "Jay": os.environ['Jay'],      # Replace with Jay's actual ID
    "Sushant": os.environ['Sushant']   # Replace with Sushant's actual ID
}


# ---------- Day Counter Logic ----------
def get_day_count(name: str) -> int:
    if not os.path.exists("counter.json"):
        with open("counter.json", "w") as f:
            json.dump({"Gaurav": 1, "Jay": 1, "Sushant": 1}, f)

    with open("counter.json", "r") as f:
        data = json.load(f)
        return data.get(name, 1)

def increment_day(name: str):
    with open("counter.json", "r+") as f:
        data = json.load(f)
        data[name] = data.get(name, 1) + 1
        f.seek(0)
        json.dump(data, f)
        f.truncate()

# ---------- AI Roast Generator ----------
def get_roast(name: str, day: int) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json"
    }

    prompt = (
        f"Give a witty one-line financial roast for a friend named {name}. "
        f"Mention it's Day {day} and they are still broke/not a founder/not a millionaire/not a billionaire/rat race participant"
        f"Make it startup/wealth themed. Keep it funny, witty, and sarcastic and offensive and brutal as hell."
    )

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        res = requests.post(url, headers=headers, json=data)
        res.raise_for_status()
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"OpenRouter API error: {e}")
        return f"{name} — still not a founder on Day {day}."

# ---------- Roast Sending ----------
async def send_roast(name: str):
    day = get_day_count(name)
    roast = get_roast(name, day)
    channel = bot.get_channel(CHANNEL_ID)

    user_mention = f"<@{USER_IDS[name]}>"  # Get the mention using user ID
    roast_with_mention = roast.replace(name, user_mention, 1)  # Replace name with mention

    if isinstance(channel, discord.TextChannel):
        await channel.send(roast_with_mention)
        increment_day(name)



# ---------- Scheduled Tasks ----------
@tasks.loop(time=[time(hour=4, minute=30)])  # 10 AM IST
# @tasks.loop(minutes=10)
async def roast_gaurav():
    await send_roast("Gaurav")

@tasks.loop(time=[time(hour=10, minute=30)])  # 4 PM IST
async def roast_jay():
    await send_roast("Jay")

# @tasks.loop(minutes=1)
@tasks.loop(time=[time(hour=15, minute=30)])  # 9 PM IST
async def roast_sushant():
    await send_roast("Sushant")

# ---------- Bot Events ----------
@bot.event
async def on_ready():
    print(f"{bot.user} is online.")
    roast_gaurav.start()
    roast_jay.start()
    roast_sushant.start()

# ---------- Manual Check ----------
@bot.command()
async def day(ctx):
    response = "\n".join([
        f"📅 Gaurav: Day {get_day_count('Gaurav')}",
        f"📅 Jay: Day {get_day_count('Jay')}",
        f"📅 Sushant: Day {get_day_count('Sushant')}",
    ])
    await ctx.send(response)

# ---------- Run Bot ----------
keep_alive()
bot.run(TOKEN)
