# BOIX-Chat

A webchat server and cli client written in python. This project was built to learn about python asyncio and websockets

## Installation

### Dependencies

`pip install -r requirements.txt`

## Running the Server

`python3 server.py`

## Running the Client

```bash
Useage:

python3 client.py username [uri]
    - `username` a required argument that represents the name used as the chat participant
    - `uri` an optional argument that allows the client to be connected to a custom URI
```

### Running Locally

`python3 client.py Julian`

### Connecting to hosted server

`python3 client.py Julian ws://boixchat.herokuapp.com`
