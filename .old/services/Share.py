class Share:

    def __init__(self, client, rooms):
        self.rooms = []
        self.map = {}

        for rs in rooms:
            for r in rs:
                self.rooms.append(client.get_channel(r))
                self.map[r] = [client.get_channel(i) for i in rs if i != r]


    def get_share_room(self, channel):
        return self.map[channel.id]

    def __iter__(self):
        for room in self.rooms:
            yield room