import discord, asyncio, json
import on_member_update,on_member_join,on_member_remove, \
on_message, background_process,on_reaction_add


def get_data(location):
    
    with open(location, 'r') as file:
        data = json.load(file)

    return data



class DiscordBot:

    
    
    def __init__(self,location):

        self.client = discord.Client()
        self.data = get_data(location)
        self.data['admins'] = set(self.data['admins'].split())

        on_message.set_on_message(self)
        on_message.set_on_message_delete(self)
        on_member_update.set_on_member_update(self)
        on_member_join.set_on_member_join(self)
        on_member_remove.set_on_member_remove(self)
        background_process.set_background_process(self)
        on_reaction_add.set_on_reaction_add(self)


    def run(self):

        self.client.run(self.data['token'])


        


    


    
        
