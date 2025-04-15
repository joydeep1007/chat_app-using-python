import socket
import threading
import sys
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, ttk, font
from tkinter.colorchooser import askcolor
import random
from datetime import datetime

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
        self.root.title("Chat Application")
        self.root.geometry("700x600")
        self.root.minsize(600, 500)
        
        # Set theme colors
        self.bg_color = "#f0f0f0"
        self.accent_color = "#4a6ea9"
        self.text_color = "#333333"
        self.user_colors = {}
        
        # Configure fonts
        self.default_font = font.nametofont("TkDefaultFont")
        self.default_font.configure(size=10)
        self.header_font = font.Font(family="Helvetica", size=12, weight="bold")
        self.message_font = font.Font(family="Helvetica", size=10)
        
        # Configure styles
        self.style = ttk.Style()
        self.style.configure("TButton", font=("Helvetica", 10))
        self.style.configure("TFrame", background=self.bg_color)
        
        # Main frame
        self.main_frame = ttk.Frame(self.root, padding="10 10 10 10")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header frame
        self.header_frame = ttk.Frame(self.main_frame)
        self.header_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.title_label = ttk.Label(self.header_frame, text="Chat Application", font=self.header_font)
        self.title_label.pack(side=tk.LEFT)
        
        self.status_label = ttk.Label(self.header_frame, text="Disconnected", foreground="red")
        self.status_label.pack(side=tk.RIGHT)
        
        # Chat display area with custom styling
        self.chat_frame = ttk.Frame(self.main_frame)
        self.chat_frame.pack(fill=tk.BOTH, expand=True)
        
        self.chat_area = scrolledtext.ScrolledText(
            self.chat_frame, 
            wrap=tk.WORD, 
            state='disabled', 
            font=self.message_font,
            background="white",
            foreground=self.text_color,
            padx=5,
            pady=5
        )
        self.chat_area.pack(fill=tk.BOTH, expand=True)
        
        # Input area frame
        self.input_frame = ttk.Frame(self.main_frame)
        self.input_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Message input field with styling
        self.message_entry = ttk.Entry(self.input_frame, font=self.message_font)
        self.message_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.message_entry.bind("<Return>", lambda event: self.send_message())
        
        # Send button with styling
        self.send_button = ttk.Button(
            self.input_frame, 
            text="Send", 
            command=self.send_message,
            style="TButton"
        )
        self.send_button.pack(side=tk.RIGHT)
        
        # Bottom toolbar frame
        self.toolbar_frame = ttk.Frame(self.main_frame)
        self.toolbar_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Theme button
        self.theme_button = ttk.Button(
            self.toolbar_frame, 
            text="Change Theme", 
            command=self.change_theme,
            style="TButton"
        )
        self.theme_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Clear button
        self.clear_button = ttk.Button(
            self.toolbar_frame, 
            text="Clear Chat", 
            command=self.clear_chat,
            style="TButton"
        )
        self.clear_button.pack(side=tk.LEFT, padx=(0, 5))
        
        # Quit button
        self.quit_button = ttk.Button(
            self.toolbar_frame, 
            text="Quit", 
            command=self.quit_chat,
            style="TButton"
        )
        self.quit_button.pack(side=tk.RIGHT)

    def start(self):
        # Get user's name using a dialog instead of console input
        self.root.withdraw()  # Hide the main window temporarily
        self.name = simpledialog.askstring("Login", "Enter your name:", parent=self.root)
        self.root.deiconify()  # Show the main window again
        
        if not self.name or self.name.strip() == "":
            messagebox.showerror("Error", "Name cannot be empty!")
            self.quit_chat()
            return
            
        # Update window title with username
        self.root.title(f"Chat Application - {self.name}")
        
        # Assign a random color to this user
        self.my_color = self.get_random_color()
        
        # Update status
        self.status_label.config(text="Connected", foreground="green")
        
        # Send name to server
        self.socket.send(self.name.encode())
        
        # Display welcome message
        self.display_system_message(f"Welcome to the chat, {self.name}!")

        # Start receiving messages in a separate thread
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.daemon = True
        receive_thread.start()

        # Start the GUI main loop
        self.root.protocol("WM_DELETE_WINDOW", self.quit_chat)  # Handle window close event
        self.root.mainloop()

    def receive_messages(self):
        while True:
            try:
                message = self.socket.recv(1024).decode()
                self.display_message(message)
            except:
                self.display_system_message("Connection to server lost")
                self.status_label.config(text="Disconnected", foreground="red")
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
        
        # Add timestamp
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_area.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Check if this is a system message or a user message
        if ":" in message:
            # This is a user message
            name, content = message.split(":", 1)
            
            # Get or assign color for this user
            if name not in self.user_colors:
                self.user_colors[name] = self.get_random_color()
            user_color = self.user_colors[name]
            
            # Configure tags for this message
            tag_name = f"user_{name}"
            self.chat_area.tag_configure(tag_name, foreground=user_color, font=self.message_font)
            
            # Insert the username with its color
            self.chat_area.insert(tk.END, f"{name}", tag_name)
            self.chat_area.insert(tk.END, f": {content}\n")
        else:
            # This is a system message
            self.chat_area.insert(tk.END, f"{message}\n", "system_message")
        
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)
        
    def display_system_message(self, message):
        self.chat_area.config(state='normal')
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.chat_area.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.chat_area.insert(tk.END, f"{message}\n", "system_message")
        self.chat_area.config(state='disabled')
        self.chat_area.see(tk.END)

    def quit_chat(self):
        try:
            # Try to send a quit message to the server
            self.socket.send("quit".encode())
        except:
            pass  # Socket might already be closed
        finally:
            self.socket.close()
            self.root.destroy()
            sys.exit()
            
    def change_theme(self):
        # Let user pick a new color
        color = askcolor(title="Choose Theme Color")[1]
        if color:
            self.accent_color = color
            # Update UI elements with the new color
            self.root.configure(background=color)
            self.display_system_message(f"Theme color changed to {color}")
    
    def clear_chat(self):
        self.chat_area.config(state='normal')
        self.chat_area.delete(1.0, tk.END)
        self.chat_area.config(state='disabled')
        self.display_system_message("Chat history cleared")
    
    def get_random_color(self):
        # Generate a random color that's not too light (for readability)
        r = random.randint(0, 150)
        g = random.randint(0, 150)
        b = random.randint(0, 150)
        return f"#{r:02x}{g:02x}{b:02x}"

if __name__ == "__main__":
    client = ChatClientGUI()
    client.start()
