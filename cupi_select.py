import discord
import sys
from ast import literal_eval

class SelectVote(discord.ui.Select):
    """menu deroulant (25 options max)"""
    print("select vote")
    def __init__(self, players):
        self.players = players
        options = []
        for player in self.players:
            options.append(discord.SelectOption(label=f"{player.name}"))
        super().__init__(placeholder="Select an option",max_values=-2,min_values=2,options=options)

    async def callback(self, interaction: discord.Interaction):
        """renvoie une réponse à la selection d'un choix """
        await interaction.response.defer()
        choice = self.values[0]  # type str
        voteur = await user_to_player(interaction.user, self.players)  # type player
        for personne_votee in self.players:  # type player et type liste
            await self.sys_vote(interaction, choice, personne_votee, voteur)

    async def sys_vote(self, interaction, choice, personne_votee, voteur):
        if choice == f"{personne_votee.name}" and voteur.previous_vote != None:
            author = interaction.user.id
            voteur.previous_vote.nvote -= 1
            voteur.previous_vote = personne_votee
            personne_votee.nvote += 1
            if self.player == None:
                await interaction.followup.send(
                    f"<@{author}> a voté pour <@{personne_votee.id}>. **{personne_votee.nvote}** vote(s)")
            elif self.player.role == "Voyante":
                await interaction.followup.send(f"Vous avez décidé d'espionner **{personne_votee.name}**.")
            elif self.player.role == "Loup Garou":
                await interaction.followup.send(f"<@{author}> veut dévorer **{personne_votee.name}**. **{personne_votee.nvote}** vote(s)")
            elif self.player.role == "Sorciere":
                await interaction.followup.send(f"Vous avez décidé de tuer **{personne_votee.name}**.")

        elif interaction.response.is_done() == False:
            if choice == f"{personne_votee.name}" and personne_votee.previous_vote == None:
                author = interaction.user.id
                voteur.previous_vote = personne_votee
                personne_votee.nvote += 1
                if self.player.role == None:
                    await interaction.response.send_message( f"<@{author}> a voté pour <@{personne_votee.id}>. **{personne_votee.nvote}** vote(s)", ephemeral=False)
                elif self.player.role == "Voyante":
                    await interaction.response.send_message(f"Vous avez décidé d'espionner **{personne_votee.name}**.", ephemeral=False)
                elif self.player.role == "Loup Garou":
                    await interaction.response.send_message(f"<@{author}> veut dévorer **{personne_votee.name}**. **{personne_votee.nvote}** vote(s)", ephemeral=False)
                elif self.player.role == "Sorciere":
                    await interaction.response.send_message(f"Vous avez décidé de tuer **{personne_votee.name}**.", ephemeral=False)
        else:
            if choice == f"{personne_votee.name}" and personne_votee.previous_vote == None:
                author = interaction.user.id
                voteur.previous_vote = personne_votee
                personne_votee.nvote += 1
                if self.player == None:
                    await interaction.followup.send(f"<@{author}> a voté pour <@{personne_votee.id}>. **{personne_votee.nvote}** vote(s)")
                elif self.player.role == "Voyante":
                    await interaction.followup.send(f"Vous avez décidé d'espionner **{personne_votee.name}**.")
                elif self.player.role == "Loup Garou":
                    await interaction.followup.send(f"<@{author}> veut dévorer **{personne_votee.name}**. **{personne_votee.nvote}** vote(s)")
                elif self.player.role == "Sorciere":
                    await interaction.followup.send(f"Vous avez décidé de tuer **{personne_votee.name}**.")

class SelectView(discord.ui.View):
    """permet d'afficher le menu deroulant"""
    print("select view")
    def __init__(self, players, player=None, *, timeout = 180): #Select est la classe a afficher
        super().__init__(timeout=timeout)
        self.add_item(SelectVote(players, player))

async def user_to_player(user, players: list):
    for player in players:
        if player.name == str(user):
            return player

def str_to_class(classname):
    print(getattr(sys.modules[__name__], classname)())
    return getattr(sys.modules[__name__], classname)


