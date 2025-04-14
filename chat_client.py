import socket
import threading
import sys
import tkinter as tk
from tkinter import scrolledtext

class ChatClient:
    def __init__(self, host='localhost', port=5555):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((host, port))
        except:
            print("Could not connect to server")
            sys.exit()

class ChatClientGUI(ChatClient):
    def __init__(self, host='localhost', port=5555):
        super().__init__(host, port)
        self.root = tk.Tk()
        self.root.title("Chat Client")

        # Chat display area
        self.chat_area = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, state='disabled', height=20, width=50)
        self.chat_area.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

        # Message input field
        self.message_entry = tk.Entry(self.root, width=40)
        self.message_entry.grid(row=1, column=0, padx=10, pady=10)
        self.message_entry.bind("<Return>", lambda event: self.send_message())

        # Send button
        self.send_button = tk.Button(self.root, text="Send", command=self.send_message)
        self.send_button.grid(row=1, column=1, padx=10, pady=10)

        # Quit button
        self.quit_button = tk.Button(self.root, text="Quit", command=self.quit_chat)
        self.quit_button.grid(row=2, column=0, columnspan=2, pady=10)

    def start(self):
        # Get user's name
        self.name = input("Enter your name: ")
        self.socket.send(self.name.encode())

        # Start receiving messages in a separate thread
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

        # Start the GUI main loop
        self.root.mainloop()

    def receive_messages(self):
        while True:
            try:
                message = self.socket.recv(1024).decode()
                self.display_message(message)
            except:
                self.display_message("Connection to server lost")
                self.socket.close()
                break

    def send_message(self):
        message = self.message_entry.get()
        if message.strip():
            try:
                self.socket.send(message.encode())
                self.message_entry.delete(0, tk.END)
                if message.lower() == 'quit':
                    self.quit_chat()
            except:
                self.display_message("Connection to server lost")
                self.socket.close()

    def display_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + '\n')
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)

    def quit_chat(self):
        self.socket.close()
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    client = ChatClientGUI()
    client.start()
