import disnake
from disnake.ext import commands
from modules import ticket_creator, ticket_closer, ticket_panel, ticket_commands
from config import TOKEN

intents = disnake.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

ticket_commands.setup(bot)
ticket_creator.setup(bot)
ticket_closer.setup(bot)
ticket_panel.setup(bot)

@bot.event
async def on_ready():
    print(f"Бот запущен как {bot.user}")

bot.run(TOKEN)
