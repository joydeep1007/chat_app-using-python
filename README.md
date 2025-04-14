# Chat Server

A simple multi-threaded chat server implementation in Python using sockets.

## Features

- Multi-client support using threading
- Real-time message broadcasting
- Automatic client connection/disconnection handling
- Comprehensive logging system

## Requirements

- Python 3.x
- No additional packages required (uses standard library only)

## Usage

1. Start the server:
```bash
python chat_server.py
```

2. The server will start on localhost:5555 by default

## Technical Details

### Server Architecture

- Uses TCP/IP protocol (socket.AF_INET, socket.SOCK_STREAM)
- Threaded client handling for concurrent connections
- Maintains a dictionary of active client connections
- Built-in logging for monitoring and debugging

### Message Protocol

- Messages are encoded/decoded using UTF-8
- Maximum message size: 1024 bytes
- First message from client should be their username
- Server broadcasts join/leave notifications automatically

### Error Handling

- Graceful handling of client disconnections
- Exception logging for debugging
- Automatic cleanup of disconnected clients

## Configuration

You can modify the host and port by changing the ChatServer initialization:

```python
server = ChatServer(host='your_host', port=your_port)
```

## Logging

The server logs include:
- Client connections/disconnections
- Message broadcasts
- Error events

Format: `timestamp - log_level - message`

## License

MIT License
