import asyncio

class EventHub:
    def __init__(self):
        self.clients = set()
        self.lock = asyncio.Lock()
        self.main_loop = None   # ← ADD THIS

    def set_main_loop(self, loop):
        self.main_loop = loop

    async def connect(self, ws):
        async with self.lock:
            self.clients.add(ws)
            print("CONNECTED CLIENTS:", len(self.clients))

    async def disconnect(self, ws):
        async with self.lock:
            if ws in self.clients:
                self.clients.remove(ws)

    async def broadcast(self, message):
        async with self.lock:
            #print("BROADCAST CALLED. CLIENTS:", len(self.clients))
            dead = []
            for ws in list(self.clients):
                try:
                    await ws.send_json(message)
                except Exception as e:
                    print("SEND FAILED:", e)
                    dead.append(ws)
            for ws in dead:
            	if ws in self.clients:
                	self.clients.remove(ws)


hub = EventHub()