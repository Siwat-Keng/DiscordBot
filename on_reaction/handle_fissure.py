from services.Container import FissureContainer

async def handle_fissure(reaction, user, fissure_caches):
    if reaction.emoji == '🇱':
        if isinstance(fissure_caches[reaction.message.id], FissureContainer):
            await fissure_caches[reaction.message.id].setLith()

    elif reaction.emoji == '🇲':
        if isinstance(fissure_caches[reaction.message.id], FissureContainer):
            await fissure_caches[reaction.message.id].setMeso()

    elif reaction.emoji == '🇳':
        if isinstance(fissure_caches[reaction.message.id], FissureContainer):
            await fissure_caches[reaction.message.id].setNeo()

    elif reaction.emoji == '🇦':
        if isinstance(fissure_caches[reaction.message.id], FissureContainer):
            await fissure_caches[reaction.message.id].setAxi()
            
    elif reaction.emoji == '🇷':
        if isinstance(fissure_caches[reaction.message.id], FissureContainer):
            await fissure_caches[reaction.message.id].setReq()