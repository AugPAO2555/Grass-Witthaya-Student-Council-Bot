import discord
from discord.ext import commands
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# ========================
# LOAD TOKEN
# ========================
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# ========================
# INTENTS
# ========================
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

# ========================
# CONFIG
# ========================
DATA_FILE = "points.json"

LOG_CHANNEL_ID = 1475448056160849971

APPROVED = "<:approved:1370751335695126678>"
WAITING = "<:Waiting_for_approved:1370752766183735306>"
DENIED = "<:denied:1370751020845764671>"

LINE = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"

ALLOWED_ROLE_ID = 1430508523321688145

# ========================
# LOAD DATA
# ========================
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# ========================
# SAVE DATA
# ========================
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ========================
# TIME NOW
# ========================
def time_now():
    return datetime.now().strftime("%d/%m/%Y %H:%M")

# ========================
# FOOTER
# ========================
def footer(embed):
    embed.set_footer(
        text=f"Reborn Grass Witthaya Student Council | {time_now()}"
    )

# ========================
# CHECK PERMISSION
# ========================
def has_permission(member):
    return any(role.id == ALLOWED_ROLE_ID for role in member.roles)

# ========================
# RANK SYSTEM
# ========================
def get_rank(points):

    if points >= 800:
        return "ประธาน"
    elif points >= 500:
        return "รองประธาน"
    elif points >= 300:
        return "หัวหน้าฝ่าย"
    elif points >= 150:
        return "รองหัวหน้าฝ่าย"
    elif points >= 50:
        return "Member"
    else:
        return "Trainee"

# ========================
# LOG FUNCTION
# ========================
async def send_log(embed):

    channel = bot.get_channel(LOG_CHANNEL_ID)

    if channel:
        await channel.send(embed=embed)

# ========================
# BOT READY
# ========================
@bot.event
async def on_ready():

    print(f"Bot Online: {bot.user}")

# ========================
# POINTS COMMAND
# ========================
@bot.command()
async def points(ctx, member: discord.Member = None):

    if member is None:
        member = ctx.author

    data = load_data()

    points = data.get(str(member.id), 0)

    rank = get_rank(points)

    embed = discord.Embed(

        description=(
            f"{LINE}\n\n"
            f"{APPROVED} | {member.mention}\n\n"
            f"🏅 Rank : {rank}\n"
            f"📊 Points : {points} Work Points\n\n"
            f"{LINE}"
        ),

        color=0x2ecc71

    )

    embed.set_author(
        name="Work Points | แต้มการทำงาน"
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    footer(embed)

    await ctx.send(embed=embed)

# ========================
# ADD COMMAND
# ========================
@bot.command()
async def add(ctx, member: discord.Member, amount: int):

    if not has_permission(ctx.author):

        embed = discord.Embed(
            description=f"{DENIED} | You dont have permission to run this command!",
            color=0xe74c3c
        )

        footer(embed)

        await ctx.send(embed=embed)

        return

    data = load_data()

    user_id = str(member.id)

    before = data.get(user_id, 0)

    after = before + amount

    data[user_id] = after

    save_data(data)

    embed = discord.Embed(

        description=(
            f"{APPROVED} | เพิ่ม {amount} Work Points ให้กับ {member.mention} สำเร็จ!"
        ),

        color=0x2ecc71

    )

    embed.set_author(
        name="Work Points | แต้มการทำงาน"
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    footer(embed)

    await ctx.send(embed=embed)

    log = discord.Embed(

        title="Point Added",

        description=(
            f"{APPROVED} Point Transaction\n\n"
            f"Admin : {ctx.author.mention}\n"
            f"Target : {member.mention}\n\n"
            f"Before : {before}\n"
            f"After : {after}"
        ),

        color=0x2ecc71

    )

    footer(log)

    await send_log(log)

# ========================
# REMOVE COMMAND
# ========================
@bot.command()
async def remove(ctx, member: discord.Member, amount: int):

    if not has_permission(ctx.author):

        embed = discord.Embed(
            description=f"{DENIED} | You dont have permission to run this command!",
            color=0xe74c3c
        )

        footer(embed)

        await ctx.send(embed=embed)

        return

    data = load_data()

    user_id = str(member.id)

    before = data.get(user_id, 0)

    after = before - amount

    if after < 0:
        after = 0

    data[user_id] = after

    save_data(data)

    embed = discord.Embed(

        description=(
            f"{APPROVED} | ลบ {amount} Work Points จาก {member.mention} สำเร็จ!"
        ),

        color=0xe74c3c

    )

    embed.set_author(
        name="Work Points | แต้มการทำงาน"
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    footer(embed)

    await ctx.send(embed=embed)

    log = discord.Embed(

        title="Point Removed",

        description=(
            f"{DENIED} Point Transaction\n\n"
            f"Admin : {ctx.author.mention}\n"
            f"Target : {member.mention}\n\n"
            f"Before : {before}\n"
            f"After : {after}"
        ),

        color=0xe74c3c

    )

    footer(log)

    await send_log(log)

# ========================
# DUTY COMMAND (MINUTES)
# ========================
@bot.command()
async def duty(ctx, member: discord.Member, minutes: int):

    if not has_permission(ctx.author):

        embed = discord.Embed(
            description=f"{DENIED} | You dont have permission to run this command!",
            color=0xe74c3c
        )

        footer(embed)

        await ctx.send(embed=embed)

        return

    points = minutes // 6

    data = load_data()

    user_id = str(member.id)

    before = data.get(user_id, 0)

    after = before + points

    data[user_id] = after

    save_data(data)

    embed = discord.Embed(

        description=(
            f"{APPROVED} | เพิ่ม {points} Work Points ให้กับ {member.mention}\n\n"
            f"⏱️ Minutes : {minutes}"
        ),

        color=0x3498db

    )

    embed.set_author(
        name="Work Points | แต้มการทำงาน"
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    footer(embed)

    await ctx.send(embed=embed)

    log = discord.Embed(

        title="Duty Points Added",

        description=(
            f"{APPROVED} Duty Transaction\n\n"
            f"Admin : {ctx.author.mention}\n"
            f"Target : {member.mention}\n\n"
            f"Minutes : {minutes}\n"
            f"Points : {points}\n\n"
            f"Before : {before}\n"
            f"After : {after}"
        ),

        color=0x3498db

    )

    footer(log)

    await send_log(log)

# ========================
# RUN
# ========================
bot.run(TOKEN)
