from typing import List, Optional
import discord
from discord.components import SelectOption
from discord.ui import Button, View
from discord.ext import commands
import json

intents = discord.Intents.all()
intents.typing = False
intents.presences = False

with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    
TOKEN = config['token']
PREFIX = config['prefix']

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

class CloseButton(Button):
    def __init__(self):
        super().__init__(label="Fechar Ticket", custom_id="close_ticket", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        await interaction.message.channel.delete()
        embed = discord.Embed(
            description='Seu ticket foi fechado. Se precisar de mais ajuda, sinta-se à vontade para abrir um novo ticket!', 
            color=0x2b2d31
        )
        embed.set_author(name=f'{interaction.user.name} seu ticket foi finalizado!', icon_url=interaction.user.avatar.url)
        await interaction.user.send(embed=embed)

class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(value="Dúvida", label="Dúvida"),
            discord.SelectOption(value="Parceria", label="Orçamento"),
        ]
        super().__init__(
            placeholder="Selecione algo...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="persistent_view:dropdown_help"
        )

    async def callback(self, interaction: discord.Interaction):
        if not self.check_permissions(interaction.user):
            await interaction.response.send_message("Você não tem permissão para criar um ticket.")
            return

        ticket_channel_name = f'{interaction.user.name} - {interaction.user.id}'
        overwrites = {
            interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True),
            interaction.guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        ticket_channel = await interaction.guild.create_text_channel(ticket_channel_name, overwrites=overwrites)

        embed = discord.Embed(
            description=(f'\n > Forneça o máximo de detalhes possível sobre sua solicitação ou problema para que possa ser atendido da melhor maneira.\n\n- **👤 Aberto por: {interaction.user.mention}**\n- **📝 Motivo: {self.values[0]}**'),
            color=0x2b2d31
        )
        
        embed.set_author(name=f'{interaction.user.name} seja bem-vindo ao seu ticket!', icon_url=interaction.user.avatar.url)

        close_button = CloseButton()
        close_view = View(timeout=False)
        close_view.add_item(close_button)

        message = await ticket_channel.send(embed=embed)

        warning_button = Button(label='Ir ao ticket', url=f'https://discord.com/channels/{interaction.guild.id}/{ticket_channel.id}')
        warning_view = View(timeout=False)
        warning_view.add_item(warning_button)

        embed = discord.Embed(description=f'**✅ㅤSeu ticket foi criado com sucesso!**', color=0x3fbf57)
        await interaction.response.send_message(embed=embed, view=warning_view, ephemeral=True)
        await message.edit(view=close_view)

    def check_permissions(self, user: discord.User) -> bool:
        return True

@bot.command(name='setup')
async def ticket(ctx):
    view = discord.ui.View(timeout=None)
    dropdown = Dropdown()
    view.add_item(dropdown)
    
    initial_embed = discord.Embed(
        title="Abra um ticket!",
        description="Abra um ticket e escolha a opção que mais se encaixa em seu problema.",
        color=0x2b2d31
    )
    
    await ctx.send(embed=initial_embed, view=view)

@bot.event
async def on_ready():
    print(f'Bot pronto')

bot.run(TOKEN)