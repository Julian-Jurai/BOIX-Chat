import asyncio
import os
from asyncio.streams import start_server
import websockets
from http import HTTPStatus
from uuid import uuid4
from faker import Faker

HOST = os.environ.get("HOST", "localhost")
PORT = int(os.environ.get("PORT", 21003))

class HandleConnectionOpen():
	async def __call__(self, connections, connection, broadcast, **kwargs):
		message = f"Welcome {connection.username}! You are 1 of {len(connections)} members."
		await connection.send(message)
		message = f"{connection.username} has joined the chat room"
		await broadcast(message)

class HandleConnectionClosed():
	async def __call__(self, connections, connection, broadcast, **kwargs):
		message = f"{connection.username} has left the chat room"
		await broadcast(message, exclude_connections=[connection])

class HandleIncomingMessage():
	async def __call__(self, connections, connection, broadcast, message=None, **kwargs):
		if not message:
			return

		message = f"{connection.username}: {message}"
		await broadcast(message, exclude_connections=[connection])

class ConnectionManager:
	def __init__(self, on_open_handlers=[], on_close_handlers=[], on_message_handlers=[]):
		self.on_open_handlers = on_open_handlers
		self.on_close_handlers = on_close_handlers
		self.on_message_handlers = on_message_handlers
		self.connections = set()

	async def add_connection(self, connection, _path):
		"""
		Adds a new connection  and runs all functions in on_open_handlers.
		"""

		self._add_new_connection(connection)

		for handler in self.on_open_handlers:
			asyncio.create_task(handler(self.connections, connection, self.broadcast))

		try:
			await self._recieve_messages(connection)
		except websockets.exceptions.ConnectionClosedError:
			self._remove_connection(connection)

	def _add_new_connection(self, connection):
		username = connection.request_headers.get("X-USERNAME", "")

		if not username:
			username = Faker().unique.job()

		connection.username = username

		print(f"[Connection Added] {username} joined the chat room")

		self.connections.add(connection)

	def _remove_connection(self, connection):
		print(f"[Connection Closed] {connection.username} left the chat room")

		self.connections.remove(connection)

		for handler in self.on_close_handlers:
			asyncio.create_task(handler(self.connections, connection, self.broadcast))

	async def _recieve_messages(self, connection):
		async for message in connection:
			print(f"[Message Received] From: {connection.username} Message: {message}")
			msg = message.strip()
			if msg:
				for handler in self.on_message_handlers:
					asyncio.create_task(handler(self.connections, connection, self.broadcast, message=msg))

	async def broadcast(self, message, exclude_connections=[]):
		print(f"[Broadcasting] {message}")

		for connection in self.connections.difference(exclude_connections):
			try:
				await connection.send(f"{message}")
			except websockets.exceptions.ConnectionClosedError:
				self._remove_connection(connection)

class WebSocketServer:
	def start(connection_manager):
		start_server = websockets.serve(
			connection_manager.add_connection,
			HOST,
			PORT,
			process_request=WebSocketServer.process_request
		)
		print(f"Server started on ws://{HOST}:{PORT}")
		asyncio.get_event_loop().run_until_complete(start_server)
		asyncio.get_event_loop().run_forever()

	async def process_request(path, request_headers):
		"""
		Intercept requests to handle websocket connections
		or HTTP GET requests.
		See: https://websockets.readthedocs.io/en/9.0.1/_modules/websockets/legacy/server.html#WebSocketServerProtocol.process_request
		"""

		if "Upgrade" in request_headers:
			return  # Probably a WebSocket connection

		response_headers = [
			('Content-Type', 'text/plain'),
			('Connection', 'close'),
		]
		return (HTTPStatus.OK, response_headers, 'Whoops! Looking for boix eh?'.encode('utf-8'))


if __name__ == "__main__":
	connection_manager = ConnectionManager(
		on_open_handlers=[HandleConnectionOpen()],
		on_close_handlers=[HandleConnectionClosed()],
		on_message_handlers=[HandleIncomingMessage()]
	)

	server = WebSocketServer.start(connection_manager)
