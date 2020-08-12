import asyncio

def set_on_voice_state_update(bot):
    
    @bot.client.event
    async def on_voice_state_update(member, before, after):

        if member.id in bot.data['logging']:
            bot.data['logging'][member.id] += 1
        else:
             bot.data['logging'][member.id] = 1

        if bot.data['logging'][member.id] == 6:
            await member.remove_roles(bot.data['roles']['checkedIntro'])
            await bot.data['channels']['general'].send('อย่า Spam สิ {}'.format(member.mention), delete_after=60)
            await asyncio.sleep(3)
            await member.add_roles(bot.data['roles']['checkedIntro'])
            bot.data['logging'][member.id] = 0
        else:
            await asyncio.sleep(3)
            bot.data['logging'][member.id] = 0
        
