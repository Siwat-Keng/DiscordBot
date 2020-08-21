def set_on_message_delete(client, *args):

    @client.event
    async def on_message_delete(message):
        for caches in args:
            if message.id in caches:
                del caches[message.id]