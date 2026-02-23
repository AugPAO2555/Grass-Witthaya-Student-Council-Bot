import discord
from discord.ext import commands
import json
import os
from datetime import datetime
import pytz

# ========================
# TOKEN
# ========================
TOKEN = os.getenv("DISCORD_TOKEN")

# ========================
# Intents
# ========================
intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ========================
# ตั้งค่า
# ========================
DATA_FILE = "points.json"

LOG_CHANNEL_ID = 1475448056160849971

ADMIN_ROLE_ID = 1369286013255422048
MOD_ROLE_ID = 1369286013134045184

# emoji
APPROVED = "<:approved:1370751335695126678>"
WAITING = "<:Waiting_for_approved:1370752766183735306>"
DENIED = "<:denied:1370751020845764671>"

LINE = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"

# ========================
# footer time
# ========================
def get_footer():

    tz = pytz.timezone("Asia/Bangkok")
    now = datetime.now(tz)

    time_str = now.strftime("%d/%m/%Y %H:%M")

    return f"( Reborn ) Grass Witthaya Student Council | สภานักเรียนกราซวิทยา | {time_str}"


# ========================
# load data
# ========================
def load_data():

    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r") as f:
        return json.load(f)


# ========================
# save data
# ========================
def save_data(data):

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ========================
# permission check
# ========================
def has_permission(member):

    return any(
        role.id in [ADMIN_ROLE_ID, MOD_ROLE_ID]
        for role in member.roles
    )


# ========================
# send log
# ========================
async def send_log(guild, target, moderator, action, amount, new_points):

    channel = guild.get_channel(LOG_CHANNEL_ID)

    if not channel:
        return

    if action == "add":
        emoji = APPROVED
        text = f"เพิ่ม {amount}"
        color = 0x2ecc71

    else:
        emoji = APPROVED
        text = f"ลด {amount}"
        color = 0xe74c3c

    embed = discord.Embed(
        description=(
            f"{LINE}\n\n"
            f"{emoji} | Point Logs\n\n"
            f"👤 ผู้ใช้: {target.mention}\n"
            f"📊 การดำเนินการ: {text} Work Points\n"
            f"📦 แต้มคงเหลือ: **{new_points}**\n"
            f"🛡 ผู้ดำเนินการ: {moderator.mention}\n\n"
            f"{LINE}"
        ),
        color=color
    )

    embed.set_thumbnail(
        url=target.display_avatar.url
    )

    embed.set_footer(
        text=get_footer()
    )

    await channel.send(embed=embed)


# ========================
# bot ready
# ========================
@bot.event
async def on_ready():

    print(f"Bot Online: {bot.user}")


# ========================
# points command
# ========================
@bot.command()
async def points(ctx, member: discord.Member = None):

    if member is None:
        member = ctx.author

    data = load_data()

    points = data.get(str(member.id), 0)

    embed = discord.Embed(
        description=(
            f"{LINE}\n\n"
            f"{APPROVED} | {member.mention} มี **{points} Work Points**\n\n"
            f"{LINE}"
        ),
        color=0x2ecc71
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.set_footer(
        text=get_footer()
    )

    await ctx.send(embed=embed)


# ========================
# add command
# ========================
@bot.command()
async def add(ctx, member: discord.Member, amount: int):

    if not has_permission(ctx.author):

        embed = discord.Embed(
            description=(
                f"{LINE}\n\n"
                f"{DENIED} | You dont have permission to run this command!\n\n"
                f"{LINE}"
            ),
            color=0xe74c3c
        )

        embed.set_footer(
            text=get_footer()
        )

        await ctx.send(embed=embed)

        return


    data = load_data()

    user_id = str(member.id)

    current = data.get(user_id, 0)

    new = current + amount

    data[user_id] = new

    save_data(data)

    embed = discord.Embed(
        description=(
            f"{LINE}\n\n"
            f"{APPROVED} | มอบ {amount} Work Points ให้กับ {member.mention} เรียบร้อย\n\n"
            f"{LINE}"
        ),
        color=0x2ecc71
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.set_footer(
        text=get_footer()
    )

    await ctx.send(embed=embed)

    await send_log(ctx.guild, member, ctx.author, "add", amount, new)


# ========================
# remove command
# ========================
@bot.command()
async def remove(ctx, member: discord.Member, amount: int):

    if not has_permission(ctx.author):

        embed = discord.Embed(
            description=(
                f"{LINE}\n\n"
                f"{DENIED} | You dont have permission to run this command!\n\n"
                f"{LINE}"
            ),
            color=0xe74c3c
        )

        embed.set_footer(
            text=get_footer()
        )

        await ctx.send(embed=embed)

        return


    data = load_data()

    user_id = str(member.id)

    current = data.get(user_id, 0)

    new = current - amount

    if new < 0:
        new = 0

    data[user_id] = new

    save_data(data)

    embed = discord.Embed(
        description=(
            f"{LINE}\n\n"
            f"{APPROVED} | ลด {amount} Work Points จาก {member.mention} เรียบร้อย\n\n"
            f"{LINE}"
        ),
        color=0xe74c3c
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.set_footer(
        text=get_footer()
    )

    await ctx.send(embed=embed)

    await send_log(ctx.guild, member, ctx.author, "remove", amount, new)


# ========================
# run bot
# ========================
bot.run(TOKEN)