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

class HandleBotCommands():
	async def __call__(self, connections, connection, broadcast, message=None, **kwargs):
		if not message:
			return

		if message == "/whoisonline":
			await self.handle_whoisonline(connections, broadcast)


	async def handle_whoisonline(self, connections, broadcast):
		print(f"[Bot Command Invoked] /whoisonline")
		if len(connections) > 0:
			message = "Currently Online:\n"
			for connection in connections:
				message += f"- {connection.username}\n"
		else:
			message = "You are the only one here"

		await broadcast(message)
