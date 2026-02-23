import discord
from discord.ext import commands
from discord import app_commands
import os

# ========================
# ตั้งค่า TOKEN จาก Railway Environment
# ========================
TOKEN = os.getenv("TOKEN")

# ========================
# Intents
# ========================
intents = discord.Intents.all()

# ========================
# สร้าง bot
# ========================
bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# ========================
# ตรวจสอบ permission (Admin / Mod)
# ========================
def has_announce_permission(user: discord.Member):
    if user.guild_permissions.administrator:
        return True

    allowed_roles = ["Admin", "Moderator", "Mod", "Staff"]
    return any(role.name in allowed_roles for role in user.roles)

# ========================
# เมื่อ bot online
# ========================
@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

    try:
        synced = await bot.tree.sync()
        print(f"Slash commands synced: {len(synced)}")
    except Exception as e:
        print(e)

# ========================
# /ping command
# ========================
@bot.tree.command(name="ping", description="ตรวจสอบสถานะบอท")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    await interaction.response.send_message(
        f"Pong! 🏓\nLatency: {latency}ms"
    )

# ========================
# /announce command
# ========================
@bot.tree.command(name="announce", description="สร้างประกาศประชาสัมพันธ์")
@app_commands.describe(
    topic="หัวข้อประกาศ",
    date="วันที่",
    content="เนื้อหาประกาศ"
)
async def announce(interaction: discord.Interaction, topic: str, date: str, content: str):

    if not has_announce_permission(interaction.user):
        await interaction.response.send_message(
            "❌ เฉพาะ Admin หรือ Mod เท่านั้น",
            ephemeral=True
        )
        return

    LOGO = "<:GameZone_Full_Logo:1475409495856386139>"
    LINE = "▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬"

    embed = discord.Embed(
        description=(
            f"ㅤㅤㅤㅤㅤㅤㅤ❮ ประชาสัมพันธ์ {LOGO} ❯ㅤㅤㅤㅤㅤㅤㅤ\n\n"
            f"{LINE}\n\n"
            f"( Topic | หัวข้อ ) : {topic}\n"
            f"( Date | วันที่ ) : {date}\n\n"
            f"{content}\n\n"
            f"{LINE}"
        ),
        color=0x2f3136
    )

    embed.set_footer(
        text=f"ประกาศโดย {interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url
    )

    await interaction.response.send_message(embed=embed)

# ========================
# Run bot
# ========================
bot.run(TOKEN)