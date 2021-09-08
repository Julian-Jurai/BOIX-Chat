# BOIX-Chat

A webchat server and cli client written in python. This project was built to learn about python asyncio and websockets

## Installation

The application requires python 3.9 or above

### Dependencies

`pip install -r requirements.txt`

## Running the Server

`python3 server.py`

### Requirements for connecting to hosted server

## Running the Client

```bash
Useage:
  python3 client.py <username>
  python3 client.py <username> [uri]

  - `username` a required argument that represents the name used as the chat participant
  - `uri` an optional argument that allows the client to be connected to a custom URI
```

### Running Locally

`python3 client.py Julian`

### Running against hosted server

`python3 client.py Julian ws://boixchat.herokuapp.com`
