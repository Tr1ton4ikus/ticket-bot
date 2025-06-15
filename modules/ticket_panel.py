import disnake
from disnake.ext import commands
from disnake import ButtonStyle

def setup(bot):
    @bot.slash_command(name="tickets", description="Отправить панель создания тикетов (только для админов)")
    @commands.has_permissions(administrator=True)
    async def tickets(inter: disnake.ApplicationCommandInteraction):
        embed = disnake.Embed(
            title="🎟️ Открыть тикет",
            description="Нажмите кнопку ниже, чтобы открыть тикет и связаться с администрацией.",
            color=0x00ff00
        )

        view = disnake.ui.View()
        view.add_item(
            disnake.ui.Button(
                label="Открыть тикет",
                style=ButtonStyle.green,
                custom_id="create_ticket"
            )
        )

        await inter.response.send_message(embed=embed, view=view)

