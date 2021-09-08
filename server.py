import asyncio
from asyncio.streams import start_server
import websockets
from datetime import datetime
from uuid import uuid4

HOST = "localhost"
PORT = 21003

class WebSocketHandler:
	def __init__(self):
		self.connections = dict()

	async def connect(self, websocket, _path):
		username = websocket.request_headers["X-USERNAME"]
		key = f"{username}-{uuid4().hex}"
		self.connections[key] =  (websocket, username)

		print(f"[{str(datetime.now())}] [Connection Added] {username} joined the chat room")

		await self.broadcast(f"{username} has joined the chat room")

		await self.listen_for_messages(key)

	async def broadcast(self, message, sender=None, sender_key=None):
		print(f"[{str(datetime.now())}] [Broadcasting] {message}")
		for websocket, username in self.connections.values():
			if sender == username: # Skip sending to the sender
				continue
			try:
				if sender:
					await websocket.send(f"{sender}: {message}")
				else:
					await websocket.send(f"{message}")
			except websockets.exceptions.ConnectionClosedError:
				del self.connections[sender_key]
				print(f"[{str(datetime.now())}] [Connection Lost] {username} left the chat room")
				await self.broadcast(f"{username} has left the chat room")

	async def listen_for_messages(self, key):
		try:
			websocket, username = self.connections[key]
			async for message in websocket:
				await self.broadcast(message, sender=username, sender_key=key)
		except websockets.exceptions.ConnectionClosedError:
			del self.connections[key]
			print(f"[{str(datetime.now())}] [Connection Lost] {username} left the chat room")
			await self.broadcast(f"{username} has left the chat room")

ws_handler = WebSocketHandler()

start_server = websockets.serve(ws_handler.connect, HOST, PORT)
print(f"Server started on ws://{HOST}:{PORT}")
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
