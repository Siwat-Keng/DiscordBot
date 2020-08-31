from discord import Game, Status
from discord.ext import tasks
from asyncio import sleep

def set_task_1(client, world_stat):

    @tasks.loop(seconds=5.0)
    async def cambion_clock():
        try:
            game = Game(world_stat.timeCycle.get_cambion())
            await client.change_presence(activity=game)
        except:
            pass
        
    @cambion_clock.before_loop
    async def before_cambion_clock():
        await client.wait_until_ready()    

    cambion_clock.start()
