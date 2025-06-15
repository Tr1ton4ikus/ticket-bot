import disnake
import datetime

from config import LOG_CHANNEL_ID


async def close_ticket_process(bot, channel, author, reason="Причина не указана"):
    guild = channel.guild

    ticket_owner = None
    for member in guild.members:
        if member.bot:
            continue
        perms = channel.permissions_for(member)
        if perms.read_messages and perms.send_messages:
            ticket_owner = member
            break

    if ticket_owner:
        try:
            embed = disnake.Embed(
                title=f"Ваш тикет #{channel.name} был закрыт",
                description=f"**Причина:** {reason}",
                color=disnake.Color.red(),
                timestamp=datetime.datetime.utcnow()
            )
            embed.set_footer(text=f"Закрыл: {author}", icon_url=author.avatar.url if author.avatar else None)
            embed.set_thumbnail(url=author.avatar.url if author.avatar else None)
            await ticket_owner.send(embed=embed)
        except disnake.Forbidden:
            pass

    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    if log_channel:
        embed = disnake.Embed(
            title="Тикет закрыт",
            color=disnake.Color.red(),
            timestamp=datetime.datetime.utcnow()
        )
        embed.add_field(name="Тикет", value=channel.name, inline=False)
        embed.add_field(name="Закрыл", value=author.mention, inline=False)
        embed.add_field(name="Причина", value=reason, inline=False)
        embed.add_field(name="Пользователь", value=ticket_owner.mention if ticket_owner else "Не найден", inline=False)
        await log_channel.send(embed=embed)

    await disnake.utils.sleep_until(disnake.utils.utcnow() + datetime.timedelta(seconds=5))

    await channel.delete()
