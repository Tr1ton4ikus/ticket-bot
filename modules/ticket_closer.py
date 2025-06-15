import disnake
from disnake import ButtonStyle, ui
from disnake.ext import commands
import json
import os

from config import TICKET_CLOSER_ROLE_ID, ALLOW_TICKET_CREATOR_TO_CLOSE
from .ticket_log_utils import close_ticket_process


DATA_PATH = "ticket_data.json"


def get_ticket_number():
    if not os.path.exists(DATA_PATH):
        with open(DATA_PATH, "w") as f:
            json.dump({"last_ticket_number": 0}, f)

    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    data["last_ticket_number"] += 1

    with open(DATA_PATH, "w") as f:
        json.dump(data, f)

    return data["last_ticket_number"]


class ConfirmCloseView(ui.View):
    def __init__(self, bot, ticket_creator_id, channel):
        super().__init__(timeout=60)
        self.bot = bot
        self.ticket_creator_id = ticket_creator_id
        self.channel = channel

    @ui.button(label="✅ Да", style=ButtonStyle.green)
    async def confirm(self, button: ui.Button, inter: disnake.MessageInteraction):
        modal = CloseTicketModal(self.bot, self.ticket_creator_id, self.channel)
        await inter.response.send_modal(modal)

    @ui.button(label="❌ Нет", style=ButtonStyle.red)
    async def cancel(self, button: ui.Button, inter: disnake.MessageInteraction):
        await inter.response.send_message("Отмена закрытия тикета.", ephemeral=True)
        self.stop()


class CloseTicketModal(ui.Modal):
    def __init__(self, bot, ticket_creator_id, channel):
        components = [
            ui.TextInput(
                label="Причина закрытия",
                custom_id="close_reason",
                style=disnake.TextInputStyle.paragraph,
                placeholder="Напишите причину закрытия тикета",
                required=True,
                max_length=512,
            )
        ]
        super().__init__(title="Подтверждение закрытия тикета", components=components)
        self.bot = bot
        self.ticket_creator_id = ticket_creator_id
        self.channel = channel

    async def callback(self, inter: disnake.ModalInteraction):
        reason = inter.text_values["close_reason"]
        author = inter.author

        guild = inter.guild
        closer_role = guild.get_role(TICKET_CLOSER_ROLE_ID)
        has_closer_role = closer_role in author.roles if closer_role else False
        is_creator = (author.id == self.ticket_creator_id)

        if not (has_closer_role or (ALLOW_TICKET_CREATOR_TO_CLOSE and is_creator)):
            await inter.response.send_message("❌ У вас нет прав закрывать этот тикет.", ephemeral=True)
            return

        await inter.response.defer(ephemeral=True)
        await close_ticket_process(self.bot, self.channel, author, reason)


class CloseTicketView(ui.View):
    def __init__(self, bot, ticket_creator_id):
        super().__init__(timeout=None)
        self.bot = bot
        self.ticket_creator_id = ticket_creator_id

    @ui.button(label="Закрыть тикет", style=ButtonStyle.red, custom_id="close_ticket")
    async def close_ticket(self, button: ui.Button, inter: disnake.MessageInteraction):
        channel = inter.channel
        author = inter.author

        guild = inter.guild
        closer_role = guild.get_role(TICKET_CLOSER_ROLE_ID)
        has_closer_role = closer_role in author.roles if closer_role else False
        is_creator = (author.id == self.ticket_creator_id)

        if not (has_closer_role or (ALLOW_TICKET_CREATOR_TO_CLOSE and is_creator)):
            await inter.response.send_message("❌ У вас нет прав закрывать этот тикет.", ephemeral=True)
            return

        view = ConfirmCloseView(self.bot, self.ticket_creator_id, channel)
        await inter.response.send_message("Вы уверены, что хотите закрыть тикет?", view=view, ephemeral=True)


class TicketCloser(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


def setup(bot):
    bot.add_cog(TicketCloser(bot))
