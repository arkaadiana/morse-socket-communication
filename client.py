import socket
import os
import time
import tkinter as tk
from tkinter import messagebox
from dotenv import load_dotenv
from gui import MorseGUI

class MorseClient:
    def __init__(self):
        load_dotenv()
        self.SERVER_IP = os.getenv("SERVER_IP", "127.0.0.1")  # Default if not specified
        self.SERVER_PORT = int(os.getenv("SERVER_PORT", "5000"))  # Default if not specified
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_ip = None
        self.connection_status = "Disconnected"
        
    def connect(self):
        try:
            self.client_socket.connect((self.SERVER_IP, self.SERVER_PORT))
            self.client_ip = self.get_client_ip()
            self.connection_status = "Connected"
            return True
        except Exception as e:
            self.connection_status = f"Error: {str(e)}"
            print(f"Connection error: {e}")
            return False
        
    def get_client_ip(self):
        return self.client_socket.getsockname()[0]
        
    def send_message(self, morse_code):
        try:
            message = f"{morse_code}"
            self.client_socket.send(message.encode('utf-8'))
            return True
        except Exception as e:
            self.connection_status = f"Send Error: {str(e)}"
            print(f"Send error: {e}")
            return False
        
    def close(self):
        try:
            self.client_socket.close()
            self.connection_status = "Disconnected"
        except Exception as e:
            print(f"Close error: {e}")

# Main application entry point
if __name__ == "__main__":
    # Application setup
    root = tk.Tk()
    root.title("Morse Code Client")
    
    # Set app icon (optional)
    try:
        root.iconbitmap("morse_icon.ico")  # You can add an icon file
    except:
        pass  # Ignore if icon file doesn't exist
    
    # Create client
    client = MorseClient()
    
    # Try to connect
    if client.connect():
        # Create GUI
        app = MorseGUI(root, client)
        
        # Set close handler
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
                client.close()
                root.destroy()
                
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start GUI main loop
        root.mainloop()
    else:
        messagebox.showerror("Connection Error", f"Failed to connect to server at {client.SERVER_IP}:{client.SERVER_PORT}\n\n{client.connection_status}")
        root.destroy()