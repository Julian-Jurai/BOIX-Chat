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

## Debugging

### Testing Server using `curl`

```bash
curl \
    --include \
    --no-buffer \
    --header "Connection: Upgrade" \
    --header "Upgrade: websocket" \
    --header "Host: example.com:80" \
    --header "Origin: http://example.com:80" \
    --header "X-USERNAME: Julian" \
    http://example.com:80/
```
