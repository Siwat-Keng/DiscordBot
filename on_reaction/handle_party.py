from services.Container import PartyContainer

async def handle_party(reaction, user, guilds, party_caches):
    if reaction.emoji == "👍":
        if isinstance(party_caches[reaction.message.id], PartyContainer):
            await party_caches[reaction.message.id].add_member(user)

    elif reaction.emoji == "👎":
        if isinstance(party_caches[reaction.message.id], PartyContainer):
            if not await party_caches[reaction.message.id].remove_member(user):
                del party_caches[reaction.message.id]                          

    elif reaction.emoji == "📃":
        if isinstance(party_caches[reaction.message.id], PartyContainer):
            await party_caches[reaction.message.id].getMemberProfile(guilds\
                [reaction.message.guild.id].members.members)                      

    elif reaction.emoji == "🚩":
        if isinstance(party_caches[reaction.message.id], PartyContainer) and \
            user == party_caches[reaction.message.id].leader:
            party_caches[await party_caches[reaction.message.id].refresh()] = \
                party_caches[reaction.message.id]

    elif reaction.emoji == "➕":
        if isinstance(party_caches[reaction.message.id], PartyContainer):
            await party_caches[reaction.message.id].increaseSize()

    elif reaction.emoji == "➖":          
        if isinstance(party_caches[reaction.message.id], PartyContainer):
            await party_caches[reaction.message.id].decreaseSize() 