import discord
from discord import app_commands
from discord.ext import commands
import chat_exporter
import io

# ==========================================
# CONFIGURAZIONE
# ==========================================
TOKEN = "MTUyMTA3MTAwMjg5NTkxMjk5MA.GDFeHa.DegkxtVVJ3GA_FBlz33ccsZL_IL-U8h2fpJpsQ"
LOG_CHANNEL_ID = 1521073653024817274 # Canale Ticket
LOG_ASSENZE_ID = 1523582560800608336 
STAFF_ROLE_ID = 1521803006524522506
PILOTA_ROLE_ID = 1521137689456410745
CATEGORY_ID = 1522918988642779186

# Configurazione Emoji
EMOJI_HELP = "<:support:1523416086434021467>"
EMOJI_ALERT = "<a:Alert:1523005699255308399>"
EMOJI_BUG = "<:bugs:1523418226854199438>"
EMOJI_PARTNERSHIP = "<:partnership:1523020076620579018>"
EMOJI_FIA = "<:fia:1523020196594319586>"

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.all())

    async def setup_hook(self):
        self.add_view(TicketStarterView())
        self.add_view(CloseTicketView())
        await self.tree.sync()

bot = MyBot()

# ==========================================
# GESTIONE ASSENZE
# ==========================================
@bot.tree.command(name="assenza", description="Registra un'assenza per un pilota.")
async def assenza(interaction: discord.Interaction, pilota: discord.Member):
    staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
    if staff_role not in interaction.user.roles:
        return await interaction.response.send_message("❌ Accesso negato: Solo lo Staff può usare questo comando.", ephemeral=True)

    log_channel = interaction.guild.get_channel(LOG_ASSENZE_ID)
    embed = discord.Embed(
        title="🗓️ Registro Assenze Pilota",
        color=discord.Color.orange(),
        description=f"Il pilota {pilota.mention} è stato segnato come **Assente** dal sistema."
    )
    embed.add_field(name="Registrato da", value=interaction.user.mention)
    embed.set_footer(text="Developed by Davidix")
    
    await log_channel.send(embed=embed)
    await interaction.response.send_message(f"✅ Assenza registrata per {pilota.mention}.", ephemeral=True)

# ==========================================
# GESTIONE TICKET
# ==========================================
class TicketModal(discord.ui.Modal):
    def __init__(self, categoria):
        super().__init__(title=f"Richiesta: {categoria}")
        self.categoria = categoria

    pilota = discord.ui.TextInput(label="Nome Pilota (Facoltativo)", style=discord.TextStyle.short, placeholder="Es: PilotaRoblox12", required=False)
    dettagli = discord.ui.TextInput(label="Dettagli della richiesta", style=discord.TextStyle.paragraph, placeholder="Descrivi il problema...", required=True, min_length=5)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        staff_role = guild.get_role(STAFF_ROLE_ID)
        channel = await guild.create_text_channel(
            name=f"{self.categoria.lower()}-{interaction.user.name}",
            category=guild.get_channel(CATEGORY_ID),
            overwrites={guild.default_role: discord.PermissionOverwrite(read_messages=False), 
                        interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True),
                        staff_role: discord.PermissionOverwrite(read_messages=True, send_messages=True, attach_files=True)}
        )
        embed = discord.Embed(title=f"🎫 Ticket Aperto — {self.categoria}", description=f"Benvenuto {interaction.user.mention}, lo staff ti risponderà a breve.", color=discord.Color.red())
        embed.add_field(name="🏁 Pilota", value=self.pilota.value or "Non specificato")
        embed.add_field(name="📝 Descrizione", value=self.dettagli.value)
        embed.set_thumbnail(url=interaction.user.display_avatar.url)
        await channel.send(f"{interaction.user.mention} | {staff_role.mention}", embed=embed, view=CloseTicketView())
        await interaction.response.send_message(f"✅ Ticket creato: {channel.mention}", ephemeral=True)

class TicketStarterView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(placeholder="👉 Seleziona la categoria...", custom_id="ticket_select", options=[
        discord.SelectOption(label="Aiuto generale", value="Help", emoji=EMOJI_HELP),
        discord.SelectOption(label="Segnalazioni", value="Alert", emoji=EMOJI_ALERT),
        discord.SelectOption(label="Bug", value="Bug", emoji=EMOJI_BUG),
        discord.SelectOption(label="Partnership", value="Partnership", emoji=EMOJI_PARTNERSHIP),
        discord.SelectOption(label="Candidatura FIA", value="Candidatura FIA", emoji=EMOJI_FIA),
    ])
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select):
        await interaction.response.send_modal(TicketModal(categoria=select.values[0]))

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Chiudi Ticket", style=discord.ButtonStyle.danger, custom_id="close_ticket_btn", emoji="🔒")
    async def close_callback(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        transcript = await chat_exporter.export(interaction.channel)
        file = discord.File(io.BytesIO(transcript.encode()), filename=f"transcript-{interaction.channel.name}.html")
        log_channel = interaction.client.get_channel(LOG_CHANNEL_ID)
        if log_channel: await log_channel.send(f"🔒 Ticket chiuso da {interaction.user.mention}", file=file)
        await interaction.channel.delete()

@bot.tree.command(name="setup", description="Genera il pannello Ticket.")
async def setup(interaction: discord.Interaction):
    staff_role = interaction.guild.get_role(STAFF_ROLE_ID)
    if not staff_role or staff_role not in interaction.user.roles:
        return await interaction.response.send_message("❌ Solo Staff.", ephemeral=True)

    embed = discord.Embed(
        title="🎫 CENTRO ASSISTENZA UFFICIALE",
        description=(
            "Benvenuto nel sistema di supporto ufficiale!\n\n"
            "Siamo qui per aiutarti nel modo più rapido ed efficiente possibile. "
            "Per iniziare, seleziona la categoria più adatta dal menu qui sotto.\n\n"
            "**📌 Informazioni**\n"
            "• Tempi di risposta: 5 minuti - 24 ore.\n"
            "• Assistenza garantita dallo Staff.\n"
            "• Un ticket per utente: evita duplicati.\n\n"
            "**⚠️ Regole**\n"
            "• Non taggare lo Staff: ti risponderemo appena possibile.\n"
            "• Mantieni un linguaggio educato.\n"
            "• Allega prove o screenshot se necessario.\n\n"
            "--- Grazie per la pazienza e la collaborazione! ---\n"
            "Il nostro Staff farà il possibile per risponderti nel minor tempo possibile."
        ),
        color=discord.Color.red()
    )
    embed.set_footer(text="Developed by Davidix")
    await interaction.channel.send(embed=embed, view=TicketStarterView())
    await interaction.response.send_message("✅ Pannello inviato.", ephemeral=True)

bot.run(TOKEN)