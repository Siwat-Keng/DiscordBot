from services.LiveSearch import LiveSearch

async def handle_riven(reaction, user, guilds, riven_caches):
    if reaction.emoji == u'\u25C0':
        if isinstance(riven_caches[reaction.message.id], LiveSearch):
            await riven_caches[reaction.message.id].container.prev()

    elif reaction.emoji == u'\u25B6':
        if isinstance(riven_caches[reaction.message.id], LiveSearch):
            await riven_caches[reaction.message.id].container.next()

    elif reaction.emoji == "❌":    
        if isinstance(riven_caches[reaction.message.id], LiveSearch) and \
            user == riven_caches[reaction.message.id].owner:
            riven_caches[reaction.message.id].searching = False
            await reaction.message.delete() 