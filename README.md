# BOIX-Chat

A webchat server and CLI client written in python. This project was built to learn about python and asyncio.

## Installation

The application requires python 3.9 or above

### Dependencies

`pip install -r requirements.txt`

## Running the Server

`python3 server.py`

## Running the Client

```bash
Useage:
  python3 client.py
  - `uri` an optional argument that allows the client to be connected to a custom URI
```

## Running agains local server

### OSX

`python3 client.py --local`

### Windows

`py -3 client.py --local`

## Running against hosted server

### OSX

`python3 client.py --remote`

### Windows

`py -3 client.py --remote`
