from discord import app_commands, SelectOption, ButtonStyle
import discord
from discord.ext import commands 
from discord.ui import Button, View, Select
from config import DISCORD_TOKEN
import Users
import learn
import exercices
import qcm
import aiohttp
from bs4 import BeautifulSoup

# Initialisation des intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=".", intents=intents)

# Stockage minimal temporaire (sélections de cours/menus)
bot.temp_data = {}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"{bot.user} est connecté et synchronisé.")
    
    # Synchronisation automatique de tous les membres
    for guild in bot.guilds:
        for member in guild.members:
            if not member.bot:
                Users.register_user(member.id, member.name)

@bot.event
async def on_message(message):
    if not message.author.bot:
        # Enregistrement automatique dans la table users
        Users.register_user(message.author.id, message.author.name)
        
         #Vérifier si l'utilisateur a un exercice en cours
        user_id = message.author.id
        if user_id in bot.temp_data and "reponse" in bot.temp_data[user_id]:
            data = bot.temp_data[user_id]
            reponse_attendue = data["reponse"]
            reponse_user = message.content.strip().lower()
            
            if reponse_user == reponse_attendue:
                # Mettre à jour l'état dans la base
                Users.update_suivi_etat(
                    suivi_id=data["suivi_id"],
                    etat='termine'
                )
                await message.add_reaction('✅')
                await message.channel.send(f"Bravo {message.author.mention} ! Réponse correcte.")
            else:
                # Mettre à jour l'état dans la base
                Users.update_suivi_etat(
                    suivi_id=data["suivi_id"],
                    etat='echoue'
                )
                
                # Décrémenter une vie seulement pour les comptes free
                if Users.get_user_type(message.author.id) == 'free':
                    remaining = Users.decrement_vie(message.author.id)
                    if remaining > 0:
                        await message.channel.send(f"❌ Réponse incorrecte. Vies restantes: {remaining}/3")
                    else:
                        await message.channel.send("❌ Plus de vies disponibles! Réessayez dans 7 heures.")
                else:
                    await message.channel.send("❌ Réponse incorrecte. (Compte premium - pas de perte de vie)")
            
            # Supprimer les données temporaires
            del bot.temp_data[user_id]
    
    await bot.process_commands(message)

# View pour les boutons Zone
class ZoneView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zone 1", style=discord.ButtonStyle.primary, custom_id="zone1")
    async def zone1_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        bot.temp_data["zone"] = "zone1"
        await interaction.response.send_message("\U0001F4CD Vous avez sélectionné **Zone 1**.", ephemeral=True)
        await interaction.followup.send(embed=discord.Embed(
            title="\U0001F4C8 Choix du modèle",
            description="Sélectionnez un modèle météo :",
            color=discord.Color.purple()), view=ModeleView())

    @discord.ui.button(label="Zone 2", style=discord.ButtonStyle.success, custom_id="zone2")
    async def zone2_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        bot.temp_data["zone"] = "zone2"
        await interaction.response.send_message("\U0001F4CD Vous avez sélectionné **Zone 2**.", ephemeral=True)
        await interaction.followup.send(embed=discord.Embed(
            title="\U0001F4C8 Choix du modèle",
            description="Sélectionnez un modèle météo :",
            color=discord.Color.purple()), view=ModeleView())

    @discord.ui.button(label="Zone 3", style=discord.ButtonStyle.danger, custom_id="zone3")
    async def zone3_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        bot.temp_data["zone"] = "zone3"
        await interaction.response.send_message("\U0001F4CD Vous avez sélectionné **Zone 3**.", ephemeral=True)
        await interaction.followup.send(embed=discord.Embed(
            title="\U0001F4C8 Choix du modèle",
            description="Sélectionnez un modèle météo :",
            color=discord.Color.purple()), view=ModeleView())

# View pour la sélection du modèle météo
class ModeleView(View):
    def __init__(self):
        super().__init__(timeout=None)

    async def fetch_dates_and_show_menu(self, interaction: discord.Interaction, modele: str):
        bot.temp_data["modele"] = modele
        zone = bot.temp_data.get("zone")
        base_url = f"http://lesvoilesderemi.yj.lu/Discords-Gribs/{modele}/{zone}/"
        dates_set = set()

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(base_url) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")

                    for link in soup.find_all("a"):
                        href = link.get("href")
                        if href and href.endswith(".grb") and href.startswith(modele):
                            start_idx = len(modele)
                            date_part = href[start_idx:start_idx + 8]  # Date en format YYYYMMDD

                            if date_part.isdigit() and len(date_part) == 8:
                                dates_set.add(date_part)

            if dates_set:
                sorted_dates = sorted(dates_set, reverse=True)
                await interaction.response.send_message(
                    embed=discord.Embed(title="📅 Dates disponibles", description="Choisissez une date :", color=discord.Color.blurple()),
                    view=DateSelectView(sorted_dates)
                )
            else:
                await interaction.response.send_message("❌ Aucune date disponible pour ce modèle et cette zone.")
        except Exception as e:
            print(e)
            await interaction.response.send_message("❌ Erreur lors de la récupération des dates.")

    @discord.ui.button(label="ECMWF", style=discord.ButtonStyle.primary, custom_id="ecmwf")
    async def ecmwf_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.fetch_dates_and_show_menu(interaction, "ecmwf")

    @discord.ui.button(label="GFS", style=discord.ButtonStyle.success, custom_id="gfs")
    async def gfs_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.fetch_dates_and_show_menu(interaction, "gfs")

class DateSelect(Select):
    def __init__(self, dates: list[str]):
        options = [
            discord.SelectOption(label=date, value=date, description=f"Fichier GRIB pour {date}")
            for date in dates
        ]
        super().__init__(placeholder="Choisissez une date GRIB disponible", min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        
        # Récupération des infos
        zone = bot.temp_data.get("zone")
        modele = bot.temp_data.get("modele")
        date = self.values[0]

        # URL du fichier GRIB
        file_url = f"http://lesvoilesderemi.yj.lu/Discords-Gribs/{modele}/{zone}/{modele}{date}.grb"

        # Création de l'embed
        embed = discord.Embed(
            title=f"Fichier GRB pour {modele.upper()} / {zone} / {date}",
            description="Cliquez sur le lien ci-dessous pour télécharger le fichier GRIB.",
            color=discord.Color.green()
        )
        embed.add_field(name="Téléchargement", value=f"[Télécharger le fichier GRB]({file_url})", inline=False)

        # Envoi de l'embed
        await interaction.followup.send(embed=embed)

class DateSelectView(View):
    def __init__(self, dates: list[str]):
        super().__init__(timeout=60)
        self.add_item(DateSelect(dates))

# Commande Slash pour lancer le bot
@bot.tree.command()
async def lvr(interaction: discord.Interaction):
    """Commande slash pour lancer l'application"""
    view = View()
    view.add_item(Button(label="Météo", style=discord.ButtonStyle.primary, custom_id="meteo"))
    view.add_item(Button(label="Learn", style=discord.ButtonStyle.primary, custom_id="learn"))
    view.add_item(Button(label="Exercices", style=discord.ButtonStyle.primary, custom_id="exercices")) 
    await interaction.response.send_message(
        embed=discord.Embed(title="Bienvenue sur le bot Sail Practice", description="Cliquez sur les options suivantes.", color=discord.Color.blue()),
        view=view
    )

# Gérer les interactions bouton
@bot.event
async def on_interaction(interaction):
    if not interaction.user.bot:
        Users.register_user(interaction.user.id, interaction.user.name)
    
    if not interaction.type == discord.InteractionType.component:
        return

    custom_id = interaction.data["custom_id"]

    if custom_id == "start_qcm":
        await start_qcm(interaction)

    elif custom_id == "meteo":
        view = View()
        view.add_item(Button(label="Générer GRIB", style=discord.ButtonStyle.success, custom_id="gribe"))
        await interaction.response.edit_message(
            embed=discord.Embed(title="\U0001F300 Météo", description="Cliquez sur Générer GRIB pour voir les zones disponibles.", color=discord.Color.green()),
            view=view
        )
    elif custom_id == "gribe":
        embed_grib = discord.Embed(
            title="\U0001F5FA️ Carte des zones",
            description="Choisissez une zone ci-dessous :",
            color=discord.Color.teal()
        )
        embed_grib.set_image(url="https://lesvoilesderemi.yj.lu/Discords-Gribs/Zone%20grb.jpg")
        await interaction.response.send_message(embed=embed_grib, view=ZoneView())

    elif custom_id == "learn":
        thematiques = learn.get_all_thematiques()
        
        if not thematiques:
            return await interaction.response.send_message("❌ Aucune thématique trouvée.", ephemeral=True)
        
        options = [discord.SelectOption(label=f"Thématique {th}", value=th) for th in thematiques]
        view = View()
        view.add_item(SelectWithOptions(options=options, placeholder="Choisissez une thématique"))
        await interaction.response.edit_message(view=view)

    elif custom_id in ["prev", "next"]:
        data = bot.temp_data.get(interaction.user.id)
        if not data: return
        
        if custom_id == "prev" and data["index"] > 0:
            data["index"] -= 1
        elif custom_id == "next" and data["index"] < len(data["chapitres"])-1:
            data["index"] += 1
        
        # Mettre à jour le chapitre dans la base
        chapitre_id = data["chapitres"][data["index"]][0]
        Users.update_suivi_chapitre(data["suivi_id"], chapitre_id)
        
        await show_chapitre(interaction)

    elif custom_id == "retry_qcm":
        data = bot.temp_data.get(interaction.user.id)
        if not data or "qcms" not in data:
            await interaction.response.send_message("❌ Session expirée. Recommencez le cours.", ephemeral=True)
            return
        
        # Réinitialiser les réponses et l'index
        data["qcm_index"] = 0
        data["qcm_answers"] = {}
        
        # Afficher à nouveau le premier QCM
        await show_qcm(interaction)

    elif custom_id == "back_to_menu":
        view = View()
        view.add_item(Button(label="Météo", style=discord.ButtonStyle.primary, custom_id="meteo"))
        view.add_item(Button(label="Learn", style=discord.ButtonStyle.primary, custom_id="learn"))
        view.add_item(Button(label="Exercices", style=discord.ButtonStyle.primary, custom_id="exercices"))
        await interaction.response.edit_message(
            embed=discord.Embed(title="Bienvenue sur le bot Sail Practice", description="Cliquez sur les options suivantes.", color=discord.Color.blue()),
            view=view
        )
    
    elif custom_id == "exercices":
        cours_list = learn.get_all_cours()
        
        if not cours_list:
            await interaction.response.send_message("❌ Aucun cours disponible.", ephemeral=True)
            return
        
        options = [
            discord.SelectOption(
                label=cours[1][:100],
                value=str(cours[0]),
                description=f"ID: {cours[0]}"
            ) for cours in cours_list
        ]
        
        cours_select = discord.ui.Select(
            placeholder="Choisissez un cours...",
            options=options
        )
        
        async def cours_select_callback(interaction: discord.Interaction):
            cours_id = int(cours_select.values[0])
            selected_course = next((c for c in cours_list if c[0] == cours_id), None)
            
            if not selected_course:
                await interaction.response.send_message("❌ Cours introuvable.", ephemeral=True)
                return
            
            niveaux = ["Débutant", "Intermédiaire", "Avancé", "Expert"]
            options_niveaux = [discord.SelectOption(label=n, value=n) for n in niveaux]
            
            niveau_select = discord.ui.Select(
                placeholder="Choisissez une difficulté...",
                options=options_niveaux
            )
            
            async def niveau_select_callback(interaction: discord.Interaction):
                niveau = niveau_select.values[0]
                cours_titre = selected_course[1]
                exercices_list = exercices.get_exercices_by_cours_and_niveau(cours_id, niveau.lower())
                
                if not exercices_list:
                    await interaction.response.send_message(f"❌ Aucun exercice {niveau} disponible pour ce cours.", ephemeral=True)
                    return
                
                options_exercices = [
                    discord.SelectOption(
                        label=f"Exercice #{ex['ex_id']}",
                        value=str(ex['ex_id']),
                        description=ex['instruction'][:100] + "..." if len(ex['instruction']) > 100 else ex['instruction']
                    ) for ex in exercices_list
                ]
                
                exercice_select = discord.ui.Select(
                    placeholder="Choisissez un exercice...",
                    options=options_exercices
                )
                
                async def exercice_select_callback(interaction: discord.Interaction):
                    ex_id = int(exercice_select.values[0])
                    exercice = next((ex for ex in exercices_list if ex['ex_id'] == ex_id), None)
                    
                    if not exercice:
                        await interaction.response.send_message("❌ Exercice introuvable.", ephemeral=True)
                        return
                    
                    # Enregistrer le début de l'exercice dans la base
                    suivi_id = Users.enregistrer_suivi(
                        discord_id=interaction.user.id,
                        type_activite='exercice',
                        cours_id=cours_id,
                        exercice_id=ex_id,
                        etat='en_cours'
                    )
                    
                    # Stocker temporairement
                    bot.temp_data[interaction.user.id] = {
                        "ex_id": exercice['ex_id'],
                        "reponse": exercice['reponse'].lower(),
                        "suivi_id": suivi_id
                    }
                    
                    # Créer et envoyer l'embed avec l'exercice
                    embed = discord.Embed(
                        title=f"Exercice #{exercice['ex_id']} ({niveau})",
                        description=(
                            f"**Cours:** {cours_titre}\n\n"
                            f"**Instruction:**\n{exercice['instruction']}\n\n"
                            f"**Étape:**\n{exercice['etape']}"
                        ),
                        color=discord.Color.blue()
                    )
                    await interaction.response.send_message(embed=embed)
                
                exercice_select.callback = exercice_select_callback
                view_exercice = View()
                view_exercice.add_item(exercice_select)
                
                await interaction.response.edit_message(
                    content=f"Exercices disponibles pour le cours **{cours_titre}** (niveau {niveau}):",
                    view=view_exercice,
                    embed=None
                )
            
            niveau_select.callback = niveau_select_callback
            view_niveau = View()
            view_niveau.add_item(niveau_select)
            
            await interaction.response.edit_message(
                content=f"Vous avez sélectionné le cours: **{selected_course[1]}**\nChoisissez maintenant la difficulté:",
                view=view_niveau,
                embed=None
            )
        
        cours_select.callback = cours_select_callback
        view_cours = View()
        view_cours.add_item(cours_select)
        
        await interaction.response.send_message(
            "Choisissez un cours pour l'exercice:",
            view=view_cours,
            ephemeral=True
        )

    elif custom_id == "reprendre_learn":
        activite = Users.get_derniere_activite(
            interaction.user.id, 
            type_activite='learn',
            etat='en_cours'
        )
        
        if not activite:
            await interaction.response.send_message("❌ Aucun cours en cours", ephemeral=True)
            return
        
        # Charger les données du cours
        chapitres = learn.get_chapitres_by_cours_id(activite['cours_id'])
        
        if not chapitres:
            await interaction.response.send_message("❌ Cours introuvable ou sans chapitres", ephemeral=True)
            return
        
        # Trouver l'index du chapitre actuel
        index = 0
        for i, chap in enumerate(chapitres):
            if chap[0] == activite['chapitre_id']:
                index = i
                break
        
        # Stocker temporairement
        bot.temp_data[interaction.user.id] = {
            "chapitres": chapitres,
            "index": index,
            "cours_id": activite['cours_id'],
            "suivi_id": activite['suivi_id']
        }
        
        await show_chapitre(interaction)
    
    elif custom_id == "reprendre_exercice":
        activite = Users.get_derniere_activite(
            interaction.user.id, 
            type_activite='exercice',
            etat='en_cours'
        )
        
        if not activite:
            await interaction.response.send_message("❌ Aucun exercice en cours", ephemeral=True)
            return
        
        # Récupérer l'exercice
        exercice = exercices.get_exercice_by_id(activite['exercice_id'])
        
        if not exercice:
            await interaction.response.send_message("❌ Exercice introuvable", ephemeral=True)
            return
        
        # Stocker temporairement
        bot.temp_data[interaction.user.id] = {
            "ex_id": activite['exercice_id'],
            "reponse": exercice['reponse'].lower(),
            "suivi_id": activite['suivi_id']
        }
        
        # Afficher l'exercice
        embed = discord.Embed(
            title=f"Exercice #{activite['exercice_id']}",
            description=(
                f"**Instruction:**\n{exercice['instruction']}\n\n"
                f"**Étape:**\n{exercice['etape']}"
            ),
            color=discord.Color.blue()
        )
        await interaction.response.send_message(embed=embed)

class SelectWithOptions(Select):
    def __init__(self, options, placeholder):
        super().__init__(
            placeholder=placeholder,
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, interaction: discord.Interaction):
        thematique_id = self.values[0]
        niveaux = ["Débutant", "Intermédiaire", "Avancé", "Expert"]
        options = [discord.SelectOption(label=n, value=n) for n in niveaux]
        view = View()
        view.add_item(NiveauSelect(options, thematique_id))
        await interaction.response.edit_message(
            embed=discord.Embed(title=f"Thématique {thematique_id}", description="Choisissez un niveau :", color=0x00ff00),
            view=view
        )

class NiveauSelect(Select):
    def __init__(self, options, thematique_id):
        super().__init__(
            placeholder="Choisissez un niveau",
            options=options,
            min_values=1,
            max_values=1
        )
        self.thematique_id = thematique_id

    async def callback(self, interaction: discord.Interaction):
        niveau = self.values[0]
        cours_list = learn.get_cours_by_thematique_niveau(self.thematique_id, niveau)
        
        if not cours_list:
            return await interaction.response.send_message("❌ Aucun cours disponible.", ephemeral=True)
            
        view = View()
        view.add_item(CoursSelect(cours_list))
        await interaction.response.edit_message(
            embed=discord.Embed(title=f"Cours - {niveau}", color=0x00ff00),
            view=view
        )

class CoursSelect(Select):
    def __init__(self, cours_list):
        options = [
            discord.SelectOption(
                label=cours[1][:100],
                value=str(cours[0]),
                description=f"ID: {cours[0]}"
            ) for cours in cours_list
        ]
        super().__init__(placeholder="Choisissez un cours...", options=options)

    async def callback(self, interaction: discord.Interaction):
        cours_id = int(self.values[0])
        
        # Vérifier l'accès au cours
        if not Users.can_access_course(interaction.user.id, cours_id):
            await interaction.response.send_message(
                "❌ Limite de cours gratuits atteinte! (3 cours maximum)\n"
                "Passez à un compte premium pour un accès illimité.",
                ephemeral=True
            )
            return
        
        chapitres = learn.get_chapitres_by_cours_id(cours_id)
        
        if not chapitres:
            await interaction.response.send_message("❌ Cours sans chapitres disponibles.", ephemeral=True)
            return
        
        
        # Récupérer la dernière progression de l'utilisateur pour ce cours
        last_chapitre_id = learn.get_last_progression(interaction.user.id, cours_id)
        
        # Trouver l'index du dernier chapitre complété
        start_index = 0
        if last_chapitre_id:
            for i, chap in enumerate(chapitres):
                if chap[0] == last_chapitre_id:
                    start_index = i + 1 if i + 1 < len(chapitres) else i
                    break
        
        # Enregistrer le début du cours dans la base
        suivi_id = Users.enregistrer_suivi(
            discord_id=interaction.user.id,
            type_activite='learn',
            cours_id=cours_id,
            chapitre_id=chapitres[start_index][0],
            etat='en_cours'
        )
        
        bot.temp_data[interaction.user.id] = {
            "chapitres": chapitres,
            "index": start_index,
            "cours_id": cours_id,
            "suivi_id": suivi_id
        }
        
        await show_chapitre(interaction)

async def show_chapitre(interaction: discord.Interaction):
    data = bot.temp_data.get(interaction.user.id)
    if not data:
        await interaction.response.send_message("❌ Session expirée. Veuillez recommencer.", ephemeral=True)
        return
    
    chapitres = data["chapitres"]
    index = data["index"]
    cours_id = data["cours_id"]
    chapitre = chapitres[index]
    chapitre_id = chapitre[0]
    
    # Mettre à jour le chapitre dans la base (CORRECTION ICI)
    Users.update_suivi_chapitre(data["suivi_id"], chapitre_id)
    

    
    # Récupération du média associé
    media_info = learn.get_media_for_chapitre(chapitre_id)
    
    # Création de l'embed
    embed = discord.Embed(
        title=f"📖 {chapitre[1]}",
        description=chapitre[2][:2000],
        color=discord.Color.blue()
    )
    
    # Ajout du média selon son type
    if media_info:
        media_type = media_info['type']
        media_url = media_info['url']
        
        if media_type == 'image':
            embed.set_image(url=media_url)
        elif media_type == 'video':
            embed.add_field(name="🎥 Vidéo associée", value=f"[Cliquez pour voir]({media_url})", inline=False)
        elif media_type == 'pdf':
            embed.add_field(name="📄 Document PDF", value=f"[Télécharger]({media_url})", inline=False)
        else:
            embed.add_field(name="📎 Pièce jointe", value=f"[Lien]({media_url})", inline=False)
    
    # Pied de page avec numérotation
    embed.set_footer(text=f"Chapitre {index+1}/{len(chapitres)}")
    
    # Création de la vue avec les boutons
    view = View()
    
    # Bouton précédent
    prev_button = Button(
        label="◀️", 
        style=ButtonStyle.secondary, 
        custom_id="prev",
        disabled=(index == 0)
    )
    view.add_item(prev_button)
    
    # Bouton suivant
    next_button = Button(
        label="▶️", 
        style=ButtonStyle.secondary, 
        custom_id="next",
        disabled=(index == len(chapitres) - 1)
    )
    view.add_item(next_button)
    
    # Vérification si c'est le dernier chapitre du cours
    last_chapitre_id = learn.get_last_chapitre_by_order(cours_id)
    is_last_chapter = (chapitre_id == last_chapitre_id)
    
    # Ajout du bouton "Valider le cours" uniquement sur le dernier chapitre
    if is_last_chapter:
        if learn.is_course_completed(interaction.user.id, cours_id):
            status_btn = Button(
                label="✅ Cours terminé",
                style=ButtonStyle.success,
                disabled=True
            )
            view.add_item(status_btn)
        else:
            qcm_button = Button(
                label="📝 Valider le cours",
                style=ButtonStyle.success,
                custom_id="start_qcm"
            )
            view.add_item(qcm_button)
    
    # Envoi du message
    await interaction.response.edit_message(embed=embed, view=view)
    
async def start_qcm(interaction: discord.Interaction):
    data = bot.temp_data.get(interaction.user.id)
    if not data:
        await interaction.response.send_message("❌ Session expirée. Recommencez le cours.", ephemeral=True)
        return
    
    cours_id = data["cours_id"]
    qcms = learn.get_qcms_for_cours(cours_id)
    
    if not qcms:
        await interaction.response.send_message("❌ Aucun QCM disponible pour ce cours.", ephemeral=True)
        return
    
    # Enregistrer le début du QCM dans la base
    suivi_id = Users.enregistrer_suivi(
        discord_id=interaction.user.id,
        type_activite='qcm',
        cours_id=cours_id,
        chapitre_id=data["chapitres"][-1][0],
        etat='en_cours'
    )
    
    bot.temp_data[interaction.user.id]["qcms"] = qcms
    bot.temp_data[interaction.user.id]["qcm_index"] = 0
    bot.temp_data[interaction.user.id]["qcm_answers"] = {}
    bot.temp_data[interaction.user.id]["suivi_id"] = suivi_id
    
    await show_qcm(interaction)

async def evaluate_qcm(interaction: discord.Interaction):
    data = bot.temp_data.get(interaction.user.id)
    if not data or "qcms" not in data:
        await interaction.response.send_message("❌ Session expirée.", ephemeral=True)
        return

    qcms = data["qcms"]
    user_answers = data["qcm_answers"]
    total_questions = len(qcms)
    correct_answers = 0

    for qcm_item in qcms:
        q_id = qcm_item['id']
        user_answer = user_answers.get(q_id)
        bonne_reponse = int(qcm_item['bonne_reponse'])
        
        if user_answer == bonne_reponse:
            correct_answers += 1

    score = (correct_answers / total_questions) * 100
    score_min = qcms[0]['Score_min']
    is_validated = score >= score_min

    # Sauvegarder le résultat dans la base
    Users.update_suivi_etat(
        suivi_id=data["suivi_id"],
        etat='termine' if is_validated else 'echoue',
        score=score
    )
    
    # Créer l'embed de résultat
    embed = discord.Embed(
        title="📝 Résultats du QCM",
        color=discord.Color.green() if is_validated else discord.Color.red()
    )
    embed.add_field(name="Votre score", value=f"{score:.1f}%", inline=True)
    embed.add_field(name="Score minimum requis", value=f"{score_min}%", inline=True)
    embed.add_field(name="Statut", value="✅ Validé" if is_validated else "❌ Non validé", inline=False)
    
    # Décrémenter une vie en cas d'échec pour les comptes free
    if not is_validated:
        account_type = Users.get_user_type(interaction.user.id)
        if account_type == 'free':
            remaining = Users.decrement_vie(interaction.user.id)
            if remaining > 0:
                embed.add_field(name="Vies restantes", value=f"{remaining}/3", inline=False)
            else:
                embed.add_field(name="Vies restantes", value="0/3 - Réessayez dans 7 heures", inline=False)
    
    # Créer la vue avec les boutons appropriés
    view = View()
    
    if is_validated:
        menu_button = Button(
            label="🏠 Retour au menu",
            style=ButtonStyle.primary,
            custom_id="back_to_menu"
        )
        view.add_item(menu_button)
    else:
        retry_button = Button(
            label="🔄 Refaire un essai", 
            style=ButtonStyle.secondary, 
            custom_id="retry_qcm"
        )
        view.add_item(retry_button)

    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

class QCMView(View):
    def __init__(self, data, qcm_item):
        super().__init__(timeout=120)
        self.data = data
        self.qcm_item = qcm_item
        self.initialize_buttons()

    def initialize_buttons(self):
        options = [
            self.qcm_item['reponse_1'], self.qcm_item['reponse_2'], self.qcm_item['reponse_3'],
            self.qcm_item['reponse_4'], self.qcm_item['reponse_5'], self.qcm_item['reponse_6']
        ]
        
        saved_answer = self.data["qcm_answers"].get(self.qcm_item["id"])
        
        for idx, option in enumerate(options, start=1):
            if option:
                style = ButtonStyle.success if saved_answer == idx else ButtonStyle.secondary
                button = Button(
                    label=f"{idx}. {option[:45]}",
                    style=style,
                    custom_id=f"qcm_ans_{idx}"
                )
                button.callback = lambda i, idx=idx: self.select_answer(i, idx)
                self.add_item(button)
        
        index = self.data["qcm_index"]
        qcms = self.data["qcms"]
        
        if index > 0:
            prev_button = Button(label="◀️", style=ButtonStyle.secondary)
            prev_button.callback = self.prev_question
            self.add_item(prev_button)
            
        if index < len(qcms) - 1:
            next_button = Button(label="▶️", style=ButtonStyle.primary)
            next_button.callback = self.next_question
            self.add_item(next_button)
        else:
            submit_button = Button(
                label="✅ Valider le QCM", 
                style=ButtonStyle.success,
                disabled=(saved_answer is None)
            )
            submit_button.callback = self.submit_all
            self.add_item(submit_button)

    async def select_answer(self, interaction: discord.Interaction, answer_index: int):
        self.data["qcm_answers"][self.qcm_item["id"]] = answer_index
        
        for item in self.children:
            if isinstance(item, Button) and item.custom_id and item.custom_id.startswith("qcm_ans_"):
                if item.custom_id == f"qcm_ans_{answer_index}":
                    item.style = ButtonStyle.success
                else:
                    item.style = ButtonStyle.secondary
        
        if self.data["qcm_index"] == len(self.data["qcms"]) - 1:
            for item in self.children:
                if isinstance(item, Button) and item.label == "✅ Valider le QCM":
                    item.disabled = False
        
        await interaction.response.edit_message(view=self)
    
    async def prev_question(self, interaction: discord.Interaction):
        if self.data["qcm_index"] > 0:
            self.data["qcm_index"] -= 1
            await show_qcm(interaction)
    
    async def next_question(self, interaction: discord.Interaction):
        if self.data["qcm_index"] < len(self.data["qcms"]) - 1:
            self.data["qcm_index"] += 1
            await show_qcm(interaction)
    
    async def submit_all(self, interaction: discord.Interaction):
        await evaluate_qcm(interaction)

async def show_qcm(interaction: discord.Interaction):
    data = bot.temp_data.get(interaction.user.id)
    if not data or "qcms" not in data:
        await interaction.response.send_message("❌ Session expirée.", ephemeral=True)
        return
    
    qcms = data["qcms"]
    index = data["qcm_index"]
    qcm_item = qcms[index]
    
    embed = discord.Embed(
        title=f"QCM {index+1}/{len(qcms)}",
        description=qcm_item['question'],
        color=discord.Color.blue()
    )
    embed.set_footer(text=f"Score minimum requis: {qcm_item['Score_min']}%")
    
    view = QCMView(data, qcm_item)
    await interaction.response.edit_message(embed=embed, view=view)

class ReprendreTypeView(View):
    def __init__(self):
        super().__init__()
        self.add_item(Button(
            label="Cours (Learn)", 
            style=ButtonStyle.primary, 
            custom_id="reprendre_learn"
        ))
        self.add_item(Button(
            label="Exercices", 
            style=ButtonStyle.secondary, 
            custom_id="reprendre_exercice"
        ))

# Gestion des cours
@bot.tree.command(name="creer_cours", description="Crée un nouveau cours")
@app_commands.describe(titre="Titre du cours", thematique="Thématique du cours", niveau="Niveau du cours")
@app_commands.choices(niveau=[
    app_commands.Choice(name="Débutant", value="débutant"),
    app_commands.Choice(name="Intermédiaire", value="intermédiaire"),
    app_commands.Choice(name="Avancé", value="avancé"),
    app_commands.Choice(name="Expert", value="expert")
])
async def creer_cours(interaction: discord.Interaction, titre: str, thematique: str, niveau: app_commands.Choice[str]):
    success = learn.ajouter_cours(titre, thematique, niveau.value)
    if success:
        await interaction.response.send_message(f"✅ Cours '{titre}' créé avec succès!")
    else:
        await interaction.response.send_message("❌ Erreur lors de la création du cours.")

@bot.tree.command(name="modifier_cours", description="Modifie un cours existant")
@app_commands.describe(cours_id="ID du cours", titre="Nouveau titre du cours", thematique="Nouvelle thématique du cours", niveau="Nouveau niveau du cours")
@app_commands.choices(niveau=[
    app_commands.Choice(name="Débutant", value="débutant"),
    app_commands.Choice(name="Intermédiaire", value="intermédiaire"),
    app_commands.Choice(name="Avancé", value="avancé"),
    app_commands.Choice(name="Expert", value="expert")
])
async def modifier_cours(interaction: discord.Interaction, cours_id: int, titre: str, thematique: str, niveau: app_commands.Choice[str]):
    success = learn.mod_cours(cours_id, titre, thematique, niveau.value)
    if success:
        await interaction.response.send_message(f"✅ Cours ID '{cours_id}' modifié avec succès!")
    else:
        await interaction.response.send_message("❌ Erreur lors de la modification du cours.")

@bot.tree.command(name="supprimer_cours", description="Supprime un cours existant")
@app_commands.describe(cours_id="ID du cours à supprimer")
async def supprimer_cours(interaction: discord.Interaction, cours_id: int):
    if interaction.guild:
        await interaction.response.send_message("❌ Utilisez cette commande en message privé (DM).", ephemeral=True)
        return

    success = learn.supr_cours(cours_id)
    if success:
        await interaction.response.send_message(f"✅ Cours ID {cours_id} supprimé !")
    else:
        await interaction.response.send_message("❌ Erreur : ID invalide ou problème SQL.")

# Gestion des chapitres
@bot.tree.command(name="ajouter_chapitre", description="Ajoute un chapitre avec un ordre spécifique")
@app_commands.describe(cours_id="ID du cours", titre="Titre du chapitre (max 250 caractères)", contenu="Contenu du chapitre", ordre="Position du chapitre (1, 2, 3...)")
async def ajouter_chapitre(interaction: discord.Interaction, cours_id: int, titre: str, contenu: str, ordre: int):
    if ordre < 1:
        return await interaction.response.send_message("❌ L'ordre doit être un nombre positif.", ephemeral=True)

    success = learn.add_chapitre(cours_id, titre, contenu, ordre)
    if success:
        await interaction.response.send_message(f"✅ Chapitre ajouté en position {ordre} !")
    else:
        await interaction.response.send_message("❌ Erreur : Ordre déjà utilisé ou problème SQL.")

@bot.tree.command(name="modifier_chapitre", description="Modifie un chapitre existant")
@app_commands.describe(
    chapitre_id="ID du chapitre à modifier",
    nouveau_titre="Nouveau titre (optionnel)",
    nouveau_contenu="Nouveau contenu (optionnel)",
    nouvel_ordre="Nouvelle position (optionnel)"
)
async def modifier_chapitre(interaction: discord.Interaction, chapitre_id: int, nouveau_titre: str = None, nouveau_contenu: str = None, nouvel_ordre: int = None):
    if nouvel_ordre is not None and nouvel_ordre < 1:
        return await interaction.response.send_message("❌ L'ordre doit être un nombre positif.", ephemeral=True)

    success = learn.mod_chapitre(chapitre_id, nouveau_titre, nouveau_contenu, nouvel_ordre)
    if success:
        await interaction.response.send_message(f"✅ Chapitre ID {chapitre_id} modifié !")
    else:
        await interaction.response.send_message("❌ Erreur : ID invalide, ordre conflictuel ou données identiques.")

@bot.tree.command(name="supprimer_chapitre", description="Supprime un chapitre par son ID")
@app_commands.describe(chapitre_id="ID numérique du chapitre à supprimer")
async def supprimer_chapitre(interaction: discord.Interaction, chapitre_id: int):
    success = learn.suppr_chapitre(chapitre_id)
    if success:
        await interaction.response.send_message(f"✅ Chapitre ID {chapitre_id} supprimé !")
    else:
        await interaction.response.send_message("❌ Erreur : ID invalide ou problème SQL.")

# Gestion des médias
@bot.tree.command(name="pj_ajouter", description="Ajoute un média à la bibliothèque")
@app_commands.describe(
    type_pj="Type de pièce jointe",
    url="URL du média"
)
@app_commands.choices(type_pj=[
    app_commands.Choice(name="Image", value="image"),
    app_commands.Choice(name="Vidéo", value="video"),
    app_commands.Choice(name="PDF", value="pdf"),
    app_commands.Choice(name="Autre", value="autre")
])
async def ajouter_pj(interaction: discord.Interaction, type_pj: app_commands.Choice[str], url: str):
    media_id = learn.add_media(url, type_pj.value)
    if media_id:
        embed = discord.Embed(
            title="✅ Média ajouté",
            description=f"ID: `{media_id}`\nType: `{type_pj.name}`",
            color=discord.Color.green()
        )
        embed.add_field(name="URL", value=url)
    else:
        embed = discord.Embed(
            title="❌ Erreur",
            description="Échec de l'ajout du média",
            color=discord.Color.red()
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="pj_modifier", description="Modifie un média existant")
@app_commands.describe(
    media_id="ID du média à modifier",
    nouveau_type="Nouveau type (optionnel)",
    nouvelle_url="Nouvelle URL (optionnel)"
)
@app_commands.choices(nouveau_type=[
    app_commands.Choice(name="Image", value="image"),
    app_commands.Choice(name="Vidéo", value="video"),
])
async def modifier_pj(interaction: discord.Interaction, media_id: int, nouveau_type: app_commands.Choice[str] = None, nouvelle_url: str = None):
    success = learn.modify_media(media_id, nouvelle_url, nouveau_type.value if nouveau_type else None)
    if success:
        embed = discord.Embed(
            title="✅ Média modifié",
            description=f"ID: `{media_id}`",
            color=discord.Color.blue()
        )
        if nouvelle_url: embed.add_field(name="Nouvelle URL", value=nouvelle_url)
        if nouveau_type: embed.add_field(name="Nouveau type", value=nouveau_type.name)
    else:
        embed = discord.Embed(
            title="❌ Erreur",
            description="Média introuvable ou données invalides",
            color=discord.Color.red()
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="pj_supprimer", description="Supprime un média de la bibliothèque")
@app_commands.describe(media_id="ID du média à supprimer")
async def supprimer_pj(interaction: discord.Interaction, media_id: int):
    success = learn.delete_media(media_id)
    embed = discord.Embed(
        title="✅ Média supprimé" if success else "❌ Erreur",
        description=f"ID: `{media_id}`" if success else "Média introuvable",
        color=discord.Color.green() if success else discord.Color.red()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Liaison médias-chapitres
@bot.tree.command(name="chapitre_ajouter_media", description="Lie un média existant à un chapitre")
@app_commands.describe(
    chapitre_id="ID du chapitre",
    media_id="ID du média à associer"
)
async def ajouter_media_chapitre(interaction: discord.Interaction, chapitre_id: int, media_id: int):
    success = learn.link_media_to_chapitre(chapitre_id, media_id)
    embed = discord.Embed(
        title="✅ Média ajouté au chapitre" if success else "❌ Erreur",
        description=f"Chapitre #{chapitre_id}\nMédia #{media_id}" if success else "ID invalide ou média inexistant",
        color=discord.Color.green() if success else discord.Color.red()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="chapitre_modifier_media", description="Change le média associé à un chapitre")
@app_commands.describe(
    chapitre_id="ID du chapitre",
    nouveau_media_id="Nouvel ID de média"
)
async def modifier_media_chapitre(interaction: discord.Interaction, chapitre_id: int, nouveau_media_id: int):
    success = learn.update_chapitre_media(chapitre_id, nouveau_media_id)
    embed = discord.Embed(
        title="✅ Média modifié" if success else "❌ Erreur",
        description=f"Nouveau média #{nouveau_media_id}" if success else "Chapitre ou média introuvable",
        color=discord.Color.blue() if success else discord.Color.red()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.tree.command(name="chapitre_supprimer_media", description="Supprime le média associé à un chapitre")
@app_commands.describe(chapitre_id="ID du chapitre")
async def supprimer_media_chapitre(interaction: discord.Interaction, chapitre_id: int):
    success = learn.remove_media_from_chapitre(chapitre_id)
    embed = discord.Embed(
        title="✅ Média supprimé" if success else "❌ Aucun média associé",
        description=f"Chapitre #{chapitre_id}",
        color=discord.Color.orange() if success else discord.Color.red()
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Gestion des QCM
@bot.tree.command(name="qcm_add", description="Ajoute un QCM à un cours")
@app_commands.describe(
    cours_id="ID du cours associé",
    question="Texte de la question",
    bonne_reponse="Numéro de la bonne réponse (1 à 6)",
    reponse_1="Réponse 1", reponse_2="Réponse 2", reponse_3="Réponse 3",
    reponse_4="Réponse 4", reponse_5="Réponse 5", reponse_6="Réponse 6",
    score_min="Score minimum requis (%) entre 0 et 100"
)
async def qcm_add(
    interaction: discord.Interaction,
    cours_id: int,
    question: str,
    bonne_reponse: int,
    reponse_1: str,
    reponse_2: str,
    reponse_3: str,
    reponse_4: str,
    reponse_5: str,
    reponse_6: str,
    score_min: int  
):
    if not (1 <= bonne_reponse <= 6):
        return await interaction.response.send_message("❌ La bonne réponse doit être entre 1 et 6.", ephemeral=True)

    if not (0 <= score_min <= 100):
        return await interaction.response.send_message("❌ Le score minimum doit être entre 0 et 100.", ephemeral=True)

    success = qcm.add_qcm(
        cours_id, 1, question, bonne_reponse,
        reponse_1, reponse_2, reponse_3,
        reponse_4, reponse_5, reponse_6,
        score_min 
    )

    await interaction.response.send_message(
        "✅ QCM ajouté avec succès." if success else "❌ Erreur SQL lors de l'ajout.", ephemeral=True
    )

@bot.tree.command(name="qcm_delete", description="Supprime un QCM existant")
@app_commands.describe(qcm_id="ID du QCM à supprimer")
async def qcm_delete(interaction: discord.Interaction, qcm_id: int):
    success = qcm.delete_qcm(qcm_id)
    await interaction.response.send_message(
        "🗑️ QCM supprimé." if success else "❌ QCM introuvable ou erreur SQL.", ephemeral=True
    )

@bot.tree.command(name="qcm_modify", description="Modifie un QCM existant")
@app_commands.describe(
    qcm_id="ID du QCM à modifier",
    cours_id="Nouvel ID de cours associé (optionnel)",
    question="Nouvelle question (optionnel)",
    bonne_reponse="Nouveau numéro de la bonne réponse (optionnel)",
    reponse_1="Réponse 1 (optionnel)", reponse_2="Réponse 2 (optionnel)", reponse_3="Réponse 3 (optionnel)",
    reponse_4="Réponse 4 (optionnel)", reponse_5="Réponse 5 (optionnel)", reponse_6="Réponse 6 (optionnel)",
    score_min="Nouveau score minimum requis (optionnel)"
)
async def qcm_modify(
    interaction: discord.Interaction,
    qcm_id: int,
    cours_id: int = None, 
    question: str = None,
    bonne_reponse: int = None,
    reponse_1: str = None,
    reponse_2: str = None,
    reponse_3: str = None,
    reponse_4: str = None,
    reponse_5: str = None,
    reponse_6: str = None,
    score_min: int = None
):
    if bonne_reponse is not None and not (1 <= bonne_reponse <= 6):
        return await interaction.response.send_message("❌ La bonne réponse doit être entre 1 et 6.", ephemeral=True)
    
    if score_min is not None and not (0 <= score_min <= 100):
        return await interaction.response.send_message("❌ Le score minimum doit être entre 0 et 100.", ephemeral=True)

    success = qcm.edit_qcm(
        qcm_id,
        question=question,
        bonne_reponse=bonne_reponse,
        reponse_1=reponse_1,
        reponse_2=reponse_2,
        reponse_3=reponse_3,
        reponse_4=reponse_4,
        reponse_5=reponse_5,
        reponse_6=reponse_6,
        score_min=score_min
    )
    
    await interaction.response.send_message(
        "✅ QCM modifié avec succès." if success else "❌ Erreur lors de la modification du QCM",
        ephemeral=True
    )

# Groupe de commandes pour les exercices
ex_group = app_commands.Group(name="ex", description="Commandes pour gérer les exercices")

@ex_group.command(name="creer", description="Créer un nouvel exercice")
@app_commands.describe(
    cours_id="ID du cours associé",
    niveau="Niveau de l'exercice",
    instruction="Instruction de l'exercice",
    etape="Étapes à suivre",
    reponse="Réponse attendue"
)
@app_commands.choices(niveau=[
    app_commands.Choice(name="Débutant", value="débutant"),
    app_commands.Choice(name="Intermédiaire", value="intermédiaire"),
    app_commands.Choice(name="Avancé", value="avancé"),
    app_commands.Choice(name="Expert", value="expert")
])
async def ex_creer(interaction: discord.Interaction, 
                 cours_id: int, 
                 niveau: app_commands.Choice[str],
                 instruction: str, 
                 etape: str, 
                 reponse: str):
    success = exercices.ajouter_exercice(cours_id, niveau.value, instruction, etape, reponse)
    if success:
        await interaction.response.send_message("✅ Exercice créé avec succès!", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Échec de la création de l'exercice.", ephemeral=True)

@ex_group.command(name="supprimer", description="Supprimer un exercice")
@app_commands.describe(ex_id="ID de l'exercice à supprimer")
async def ex_supprimer(interaction: discord.Interaction, ex_id: int):
    success = exercices.supprimer_exercice(ex_id)
    if success:
        await interaction.response.send_message(f"✅ Exercice #{ex_id} supprimé!", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Échec de la suppression. ID invalide?", ephemeral=True)

@ex_group.command(name="modifier", description="Modifier un exercice existant")
@app_commands.describe(
    ex_id="ID de l'exercice à modifier",
    cours_id="Nouvel ID de cours (optionnel)",
    niveau="Nouveau niveau (optionnel)",
    instruction="Nouvelle instruction (optionnel)",
    etape="Nouvelle étape (optionnel)",
    reponse="Nouvelle réponse (optionnel)"
)
async def ex_modifier(interaction: discord.Interaction, 
               ex_id: int, 
               cours_id: int = None,
               niveau: str = None,
               instruction: str = None,
               etape: str = None,
               reponse: str = None):
    success = exercices.modifier_exercice(
        ex_id,
        cours_id=cours_id,
        niveau=niveau,
        instruction=instruction,
        etape=etape,
        reponse=reponse
    )
    if success:
        await interaction.response.send_message(f"✅ Exercice #{ex_id} modifié avec succès!", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Échec de la modification. Vérifiez l'ID.", ephemeral=True)

@bot.tree.command(name="vies", description="Voir vos vies restantes")
async def vies(interaction: discord.Interaction):
    account_type = Users.get_user_type(interaction.user.id)
    if account_type == 'premium':
        await interaction.response.send_message(
            "🌟 Compte premium - Vies illimitées!",
            ephemeral=True
        )
    else:
        remaining = Users.get_remaining_vies(interaction.user.id)
        await interaction.response.send_message(
            f"Vous avez {remaining} vies restantes (rechargées toutes les 7 heures)",
            ephemeral=True
        )

# Ajouter le groupe de commandes au bot
bot.tree.add_command(ex_group)


bot.run(DISCORD_TOKEN)