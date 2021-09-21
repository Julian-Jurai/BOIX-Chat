import asyncio
import os
from asyncio.streams import start_server
import websockets
from http import HTTPStatus
from uuid import uuid4
from faker import Faker

HOST = os.environ.get("HOST", "localhost")
PORT = int(os.environ.get("PORT", 21003))

class WebSocketHandler:
	def __init__(self):
		self.connections = dict()

	async def connect(self, websocket, _path):
		username = websocket.request_headers.get("X-USERNAME", "")

		if not username:
			username = Faker().unique.job()

		key = f"{username}-{uuid4().hex}"
		self.connections[key] = (websocket, username)

		print(f"[Connection Added] {username} joined the chat room")

		await websocket.send(f"Welcome {username}! You are 1 of {len(self.connections)} members.")
		await self.broadcast(f"{username} has joined the chat room")

		await self.listen_for_messages(key)

	async def broadcast(self, message, sender=None, sender_key=None):
		print(f"[Broadcasting] {message}")
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
				print(f"[Connection Lost] {username} left the chat room")
				await self.broadcast(f"{username} has left the chat room")

	async def listen_for_messages(self, key):
		try:
			websocket, username = self.connections[key]
			async for message in websocket:
				msg = message.strip()
				if msg:
					await self.broadcast(msg, sender=username, sender_key=key)
					await self.handle_command(message)

		except websockets.exceptions.ConnectionClosedError:
			del self.connections[key]
			print(f"[Connection Lost] {username} left the chat room")
			await self.broadcast(f"{username} has left the chat room")

	async def process_request(server, path, request_headers):
		if "Upgrade" in request_headers:
			return  # Probably a WebSocket connection
		else:
			response_headers = [
				('Content-Type', 'text/plain'),
				('Connection', 'close'),
			]
			return (HTTPStatus.OK, response_headers, 'Whoops! Looking for boix eh?'.encode('utf-8'))

	async def handle_command(self, message):
		cmds = ["/whoisonline"]

		l = [c for c in cmds if c in message]
		cmd = l[0] if len(l) > 0 else None

		if not cmd:
			return

		if cmd == "/whoisonline":
			message = ""
			if len(self.connections.values()) > 0:
				message = "Currently Online:\n"

				for websocket, username in self.connections.values():
					message += f"- {username}\n"

			else:
				message = "You are the only one here"

			if message:
				await self.broadcast(message)

if __name__ == "__main__":
	ws_handler = WebSocketHandler()

	start_server = websockets.serve(ws_handler.connect, HOST, PORT, process_request=ws_handler.process_request)
	print(f"Server (V1) started on ws://{HOST}:{PORT}")
	asyncio.get_event_loop().run_until_complete(start_server)
	asyncio.get_event_loop().run_forever()
