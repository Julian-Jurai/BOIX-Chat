import asyncio
import os
from asyncio.streams import start_server
import websockets
from http import HTTPStatus
from uuid import uuid4
from faker import Faker

HOST = os.environ.get("HOST", "localhost")
PORT = int(os.environ.get("PORT", 21003))

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
