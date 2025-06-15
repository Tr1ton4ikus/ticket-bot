import disnake
from disnake.ext import commands
from config import TICKET_CLOSER_ROLE_ID, ALLOW_TICKET_CREATOR_TO_CLOSE
from modules.ticket_closer import close_ticket_process

def setup(bot):

    @bot.slash_command(description="Добавить пользователя в тикет")
    async def add(inter: disnake.ApplicationCommandInteraction, user: disnake.Member):
        author = inter.author
        guild = inter.guild
        channel = inter.channel

        if not channel.name.startswith("ticket-"):
            await inter.response.send_message("❌ Команда доступна только в тикет-каналах.", ephemeral=True)
            return

        closer_role = guild.get_role(TICKET_CLOSER_ROLE_ID)
        if closer_role not in author.roles:
            await inter.response.send_message("❌ У вас нет прав добавлять пользователей.", ephemeral=True)
            return

        overwrites = channel.overwrites_for(user)
        overwrites.read_messages = True
        overwrites.send_messages = True
        await channel.set_permissions(user, overwrite=overwrites)
        await inter.response.send_message(f"✅ Пользователь {user.mention} добавлен в тикет.", ephemeral=True)


    @bot.command()
    @commands.has_permissions(manage_channels=True)
    async def close(ctx, *, reason="Не указана"):
        channel = ctx.channel
        author = ctx.author

        if not channel.name.startswith("ticket-"):
            await ctx.send("Эта команда доступна только в тикет-каналах.")
            return

        closer_role = ctx.guild.get_role(TICKET_CLOSER_ROLE_ID)
        has_closer_role = closer_role in author.roles if closer_role else False

        is_creator = False
        if ALLOW_TICKET_CREATOR_TO_CLOSE:
            overwrites = channel.overwrites_for(author)
            is_creator = overwrites.read_messages and overwrites.send_messages

        if not (has_closer_role or (ALLOW_TICKET_CREATOR_TO_CLOSE and is_creator)):
            await ctx.send("❌ У вас нет прав закрывать этот тикет.")
            return

        await close_ticket_process(bot=ctx.bot, channel=channel, author=author, reason=reason)
