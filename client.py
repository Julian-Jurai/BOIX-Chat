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
		reader = asyncio.StreamReader()
		pipe = sys.stdin
		loop = asyncio.get_event_loop()
		await loop.connect_read_pipe(lambda: asyncio.StreamReaderProtocol(reader), pipe)
		async for line in reader:
			await self.connection.send(line.decode().rstrip())


if __name__ == "__main__":

	username = sys.argv[1]

	try:
		uri = sys.argv[2]
		if uri == "boix":
				uri = "ws://boixchat.herokuapp.com"
	except IndexError:
		uri = f"ws://{HOST}:{PORT}"

	client = WebSocketClient(username, uri)

	if platform.system().lower() == "windows":
			asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
	asyncio.get_event_loop().run_until_complete(client.run())
