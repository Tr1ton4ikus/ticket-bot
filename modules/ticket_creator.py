import disnake
from disnake import PermissionOverwrite, ui
from config import (
    TICKET_CATEGORY_ID, TICKET_CATEGORY_NAME,
    TICKET_ROLE_IDS, MAX_TICKETS_PER_USER
)

from modules.ticket_closer import CloseTicketView, get_ticket_number


async def create_ticket(inter: disnake.MessageInteraction, bot):
    guild = inter.guild
    user = inter.author

    category = guild.get_channel(TICKET_CATEGORY_ID)
    if not category or not isinstance(category, disnake.CategoryChannel):
        category = disnake.utils.get(guild.categories, name=TICKET_CATEGORY_NAME)
    if not category:
        category = await guild.create_category(TICKET_CATEGORY_NAME)

    existing = [
        ch for ch in category.channels
        if ch.name.startswith("ticket-") and ch.permissions_for(user).read_messages
    ]
    if len(existing) >= MAX_TICKETS_PER_USER:
        await inter.response.send_message("❌ У вас уже есть открытый тикет.", ephemeral=True)
        return

    role_ids = [r.strip() for r in TICKET_ROLE_IDS.split(",") if r.strip()]
    roles = [guild.get_role(int(rid)) for rid in role_ids if guild.get_role(int(rid))]

    ticket_number = get_ticket_number()
    channel_name = f"ticket-{ticket_number}"

    overwrites = {
        guild.default_role: PermissionOverwrite(read_messages=False)
    }
    overwrites[user] = PermissionOverwrite(read_messages=True, send_messages=True)
    for role in roles:
        overwrites[role] = PermissionOverwrite(read_messages=True, send_messages=True)

    channel = await guild.create_text_channel(channel_name, category=category, overwrites=overwrites)

    embed = disnake.Embed(
        title=f"🎫 Тикет #{ticket_number}",
        description=f"{user.mention}, ваш тикет создан. Опишите вашу проблему, и с вами свяжется поддержка.",
        color=0x00ff00
    )
    embed.set_footer(text=f"ID: {user.id}")
    embed.set_thumbnail(url=user.display_avatar.url)

    view = CloseTicketView(bot, ticket_creator_id=user.id)
    await channel.send(embed=embed, view=view)

    await inter.response.send_message(f"✅ Тикет создан: {channel.mention}", ephemeral=True)

    try:
        dm_embed = disnake.Embed(
            title="📩 Тикет создан",
            description=f"Ваш тикет под номером **#{ticket_number}** создан в {guild.name}.\n"
                        f"Ссылка: {channel.mention}",
            color=0x00ff00
        )
        dm_embed.set_thumbnail(url=user.display_avatar.url)
        await user.send(embed=dm_embed)
    except disnake.Forbidden:
        pass


def setup(bot):
    @bot.listen("on_button_click")
    async def on_button_click(inter: disnake.MessageInteraction):
        if inter.component.custom_id == "create_ticket":
            await create_ticket(inter, bot)
