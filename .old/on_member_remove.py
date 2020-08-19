def set_on_member_remove(bot):
    
    @bot.client.event
    async def on_member_remove(member):
        if member in bot.data['member_join']:
            bot.data['member_join'].remove(member)