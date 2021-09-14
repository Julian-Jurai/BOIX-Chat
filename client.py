import asyncio
import websockets
import platform
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

		reader = asyncio.StreamReader()
		pipe = sys.stdin

		if platform.system().lower() == "windows":
				# https://stackoverflow.com/questions/62412754/python-asyncio-errors-oserror-winerror-6-the-handle-is-invalid-and-runtim
				# https://bugs.python.org/issue43528
				asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

		loop = asyncio.get_event_loop()
		await loop.connect_read_pipe(lambda: asyncio.StreamReaderProtocol(reader), pipe)
		async for line in reader:
			msg = line.decode().rstrip()

			if msg:
					await self.connection.send(line.decode().rstrip())


if __name__ == "__main__":

	server =  sys.argv[1] if len(sys.argv) > 1 else "--local"

	if server == "--local":
			uri = f"ws://{HOST}:{PORT}"
	elif server == "--remote":
			uri = "ws://boixchat.herokuapp.com"

	username = input("Please enter a username: \n")

	client = WebSocketClient(username, uri)

	asyncio.get_event_loop().run_until_complete(client.run())
