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

    def update(self, client):
        self.map = { k:v for k, v in self.map.items() if client.get_channel(k) and \
            not (None in v) and v and client.get_channel(v[0].id)}
        self.rooms = [ r for r in self.rooms if r in self.map ]

    def refresh(self, client, rooms):
        self.rooms = []
        self.map = {}

        for rs in rooms:
            for r in rs:
                self.rooms.append(client.get_channel(r))
                self.map[r] = [client.get_channel(i) for i in rs if i != r]
        
    def __iter__(self):
        for room in self.rooms:
            yield room