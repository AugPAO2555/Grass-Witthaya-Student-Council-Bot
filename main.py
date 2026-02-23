import discord
from discord.ext import commands
import json
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")

# ใช้ intents ปกติ ไม่ต้อง privileged
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

DATA_FILE = "points.json"

APPROVED = "<:approved:1370751335695126678>"
LINE = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"
ALLOWED_ROLE_ID = 1430508523321688145  # role Points Givers

# ===== โหลดข้อมูล =====
def load_data():
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

# ===== บันทึกข้อมูล =====
def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


# ===== เช็ค role =====
def has_permission(member):
    return any(role.id == ALLOWED_ROLE_ID for role in member.roles)


# ===== เมื่อบอทออนไลน์ =====
@bot.event
async def on_ready():
    print(f"Student Council Bot Online: {bot.user}")


# ===== checkpoint =====
@bot.command()
async def checkpoint(ctx, member: discord.Member = None):

    if member is None:
        member = ctx.author

    data = load_data()
    points = data.get(str(member.id), 0)

    embed = discord.Embed(
        description=(
            f"{LINE}\n\n"
            f"❮ {APPROVED} ❯ | {member.name} ขณะนี้คุณมี **{points} Work Points** !\n\n"
            f"{LINE}"
        ),
        color=0x2ecc71
    )

    # ✅ thumbnail เป็น avatar user
    embed.set_thumbnail(url=member.display_avatar.url)

    await ctx.send(embed=embed)


# ===== add =====
@bot.command()
async def add(ctx, member: discord.Member, amount: int):

    if not has_permission(ctx.author):
        await ctx.send("❌ คุณไม่มีสิทธิ์ใช้คำสั่งนี้")
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
            f"❮ {APPROVED} ❯ | เพิ่ม {amount} Work Points ให้กับ **{member.name}** สำเร็จ !\n\n"
            f"{LINE}"
        ),
        color=0x2ecc71
    )

    # ✅ thumbnail avatar
    embed.set_thumbnail(url=member.display_avatar.url)

    await ctx.send(embed=embed)


# ===== remove =====
@bot.command()
async def remove(ctx, member: discord.Member, amount: int):

    if not has_permission(ctx.author):
        await ctx.send(" You dont have permission to run this command ! ")
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
            f"❮ {APPROVED} ❯ | ลบ {amount} Work Points จาก **{member.name}** สำเร็จ !\n"
            f"ขณะนี้มี {new} Work Points\n\n"
            f"{LINE}"
        ),
        color=0xe74c3c
    )

    # ✅ thumbnail avatar
    embed.set_thumbnail(url=member.display_avatar.url)

    await ctx.send(embed=embed)


bot.run(TOKEN)