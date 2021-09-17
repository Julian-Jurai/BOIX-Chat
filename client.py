import asyncio
import websockets
import sys

HOST = "localhost"
PORT = 21003

class WebSocketClient():
	def __init__(self, username, uri):
		self.username = username
		self.connection = None
		self.uri = uri

	async def run(self):
		await asyncio.gather(
			self.connect(),
			self.listen_for_messages(),
			self.listen_for_input()
		)

	async def connect(self):
		extra_headers = { "X-USERNAME": self.username }
		self.connection = await websockets.connect(self.uri, extra_headers=extra_headers)

	async def listen_for_messages(self):
		"""Listens for incoming messages"""

		while True:
			await asyncio.sleep(1)

			try:
				if self.connection:
					message = await self.connection.recv()
					print(f">> {message}")
			except websockets.exceptions.ConnectionClosedOK:
				print("Connection Closed. Attempting to reconnect...")
				await self.connect()

	async def listen_for_input(self):
		"""Listens for user input and sends value along"""
		loop = asyncio.get_event_loop()

		while True:
			line = await loop.run_in_executor(None, sys.stdin.readline)
			msg = line.rstrip()
			if msg:
				await self.connection.send(msg)

if __name__ == "__main__":

	server =  sys.argv[1] if len(sys.argv) > 1 else "--remote"

	if server == "--local":
		uri = f"ws://{HOST}:{PORT}"
	elif server == "--remote":
		uri = "ws://boixchat.herokuapp.com"

	print("""
	█░█░█ █▀▀ █░░ █▀▀ █▀█ █▀▄▀█ █▀▀   ▀█▀ █▀█
	▀▄▀▄▀ ██▄ █▄▄ █▄▄ █▄█ █░▀░█ ██▄   ░█░ █▄█

	██████╗░░█████╗░██╗██╗░░██╗  ░█████╗░██╗░░██╗░█████╗░████████╗
	██╔══██╗██╔══██╗██║╚██╗██╔╝  ██╔══██╗██║░░██║██╔══██╗╚══██╔══╝
	██████╦╝██║░░██║██║░╚███╔╝░  ██║░░╚═╝███████║███████║░░░██║░░░
	██╔══██╗██║░░██║██║░██╔██╗░  ██║░░██╗██╔══██║██╔══██║░░░██║░░░
	██████╦╝╚█████╔╝██║██╔╝╚██╗  ╚█████╔╝██║░░██║██║░░██║░░░██║░░░
	╚═════╝░░╚════╝░╚═╝╚═╝░░╚═╝  ░╚════╝░╚═╝░░╚═╝╚═╝░░╚═╝░░░╚═╝░░░
	""",end="\n\n\n")

	username = input("Please enter a username: \n")

	client = WebSocketClient(username, uri)

	asyncio.get_event_loop().run_until_complete(client.run())
