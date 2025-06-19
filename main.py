import discord
from discord.ext import tasks, commands
import os
import json
from keep_alive import keep_alive
from datetime import time, datetime, timezone
import requests

TOKEN = os.environ['DISCORD_TOKEN']
CHANNEL_ID = int(os.environ['CHANNEL_ID'])

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

USER_IDS = {
    "Gaurav": os.environ['Gaurav'],
    "Jay": os.environ['Jay'],
    "Sushant": os.environ['Sushant']
}

# ---------- Day Counter Logic ----------

START_DATE = datetime(2025, 6, 17)  # Common start date

def get_day_count():
    today = datetime.now(timezone.utc)
    delta = today.date() - START_DATE.date()
    return delta.days + 1

# ---------- AI Roast Generator ----------

def get_roast(name: str, day: int) -> str:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {os.environ['OPENROUTER_API_KEY']}",
        "Content-Type": "application/json"
    }

    prompt = (
        f"Roast a guy named {name} with a unique and creative one-liner each time. "
        f"Mention it's Day {day} and he's still not a founder, still broke, "
        f"still in the rat race, and still not a billionaire. "
        f"Include sarcastic references to startup life, tech culture, and financial delusions. "
        f"Use brutal wit and vary the style and references to avoid repetition. Pick one of the following situations and roast based on that without using the exact wording:\n"
        f"- still using ChatGPT free plan\n"
        f"- has pitch deck but no product\n"
        f"- says he's in stealth mode but actually just unemployed\n"
        f"- attends startup events with no startup\n"
        f"- thinks cold emails will save him\n"
        f"- stuck in tutorial hell\n"
        f"- even Judes is making more money\n"
        f"Make it savage, hilarious, and one-liner format. Return only the roast and keep it under 250 characters."
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
        return f"{name} — still broke on Day {day}. Even AI gave up roasting you."

# ---------- Roast Sending ----------

async def send_roast(name: str):
    day = get_day_count()
    roast = get_roast(name, day)
    channel = bot.get_channel(CHANNEL_ID)

    if channel is None:
        print(f"Channel ID {CHANNEL_ID} not found.")
        return

    user_mention = f"<@{USER_IDS[name]}>"
    roast_with_mention = roast.replace(name, user_mention, 1)

    if isinstance(channel, discord.TextChannel):
        await channel.send(roast_with_mention)

# ---------- Scheduled Tasks ----------

@tasks.loop(time=[time(hour=4, minute=30)])  # 10 AM IST
async def roast_gaurav():
    await send_roast("Sushant")

@tasks.loop(time=[time(hour=10, minute=30)])  # 4 PM IST
async def roast_jay():
    await send_roast("Jay")

@tasks.loop(time=[time(hour=16, minute=0)])  # 9.30 PM IST
async def roast_sushant():
    await send_roast("Gaurav")

# ---------- Bot Events ----------

@bot.event
async def on_ready():
    print(f"{bot.user} is online.")
    roast_gaurav.start()
    roast_jay.start()
    roast_sushant.start()

# ---------- Manual Commands ----------

@bot.command()
async def day(ctx):
    day_num = get_day_count()
    response = "\n".join([
        f"📅 Gaurav: Day {day_num}",
        f"📅 Jay: Day {day_num}",
        f"📅 Sushant: Day {day_num}",
    ])
    await ctx.send(response)

@bot.command()
async def roast(ctx, name: str):
    name = name.capitalize()
    if name not in USER_IDS:
        await ctx.send(f"❌ Unknown person: {name}")
        return
    await send_roast(name)

# ---------- Run Bot ----------
keep_alive()
bot.run(TOKEN)
