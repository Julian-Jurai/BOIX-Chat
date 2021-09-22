import asyncio
import os
from asyncio.streams import start_server
import websockets
from http import HTTPStatus
import handlers
from connection_manager import ConnectionManager

HOST = os.environ.get("HOST", "localhost")
PORT = int(os.environ.get("PORT", 21003))

class WebSocketServer:
	def start(connection_manager):
		start_server = websockets.serve(
			connection_manager.add_connection,
			HOST,
			PORT,
			process_request=WebSocketServer.process_request
		)
		print(f"Server (V2) started on ws://{HOST}:{PORT}")
		asyncio.get_event_loop().run_until_complete(start_server)
		asyncio.get_event_loop().run_forever()

	async def process_request(path, request_headers):
		"""
		Intercept requests to handle websocket connections
		or HTTP GET requests.
		See: https://websockets.readthedocs.io/en/9.0.1/_modules/websockets/legacy/server.html#WebSocketServerProtocol.process_request
		"""

		print(f"[Incoming Request] {request_headers}")

		if "Upgrade" in request_headers:
			return  # Probably a WebSocket connection

		response_headers = [
			('Content-Type', 'text/plain'),
			('Connection', 'close'),
		]
		return (HTTPStatus.OK, response_headers, 'Whoops! Looking for boix eh?'.encode('utf-8'))

if __name__ == "__main__":
	connection_manager = ConnectionManager(
		on_open_handlers=[handlers.HandleConnectionOpen()],
		on_close_handlers=[handlers.HandleConnectionClosed()],
		on_message_handlers=[handlers.HandleIncomingMessage(), handlers.HandleBotCommands()]
	)

	server = WebSocketServer.start(connection_manager)
