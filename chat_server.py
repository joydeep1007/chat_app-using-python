import socket
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ChatServer:
    def __init__(self, host='localhost', port=5555):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clients = {}  # Dictionary to store client connections
        
    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        logging.info(f"Server started on {self.host}:{self.port}")
        
        while True:
            try:
                client_socket, address = self.server_socket.accept()
                logging.info(f"New connection from {address}")
                
                # Get client name
                client_name = client_socket.recv(1024).decode()
                self.clients[client_socket] = client_name
                
                # Broadcast welcome message
                self.broadcast(f"{client_name} joined the chat!")
                
                # Start handling thread for this client
                thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                thread.daemon = True
                thread.start()
            except Exception as e:
                logging.error(f"Error accepting new connection: {e}")
            
    def handle_client(self, client_socket):
        name = self.clients.get(client_socket, "Unknown")
        
        while True:
            try:
                message = client_socket.recv(1024).decode()
                if message:
                    logging.info(f"{name}: {message}")
                    self.broadcast(f"{name}: {message}", exclude=client_socket)
                else:
                    raise Exception("Client disconnected")
            except Exception as e:
                logging.warning(f"Error with client {name}: {e}")
                self.remove_client(client_socket)
                break
                
    def broadcast(self, message, exclude=None):
        logging.info(f"Broadcasting message: {message}")
        for client in list(self.clients.keys()):
            if client != exclude:
                try:
                    client.send(message.encode())
                except Exception as e:
                    logging.warning(f"Error sending message to {self.clients[client]}: {e}")
                    self.remove_client(client)
                    
    def remove_client(self, client_socket):
        if client_socket in self.clients:
            name = self.clients[client_socket]
            del self.clients[client_socket]
            client_socket.close()
            self.broadcast(f"{name} left the chat!")
            logging.info(f"Connection with {name} closed")

if __name__ == "__main__":
    server = ChatServer()
    server.start()
