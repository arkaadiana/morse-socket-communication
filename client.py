import socket
import os
import time
import tkinter as tk
from tkinter import messagebox, simpledialog
from dotenv import load_dotenv
from gui import MorseGUI

class MorseClient:
    def __init__(self):
        # Load environment variables if available
        load_dotenv()
        
        # Get server connection details (either from .env or user input)
        self.get_connection_details()
        
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_ip = None
        self.connection_status = "Disconnected"
        
    def get_connection_details(self):
        # Check if .env values exist
        env_ip = os.getenv("SERVER_IP")
        env_port = os.getenv("SERVER_PORT")
        
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        if env_ip and env_port:
            # .env file exists with values, ask if user wants to use them
            use_env = messagebox.askyesno(
                "Connection Settings",
                f"Found server settings in .env file:\nIP: {env_ip}\nPort: {env_port}\n\nDo you want to use these settings?"
            )
            
            if use_env:
                self.SERVER_IP = env_ip
                self.SERVER_PORT = int(env_port)
            else:
                # User wants to enter new values
                self.get_user_input_for_connection()
        else:
            # No .env file or missing values, ask user to input
            self.get_user_input_for_connection()
            
        root.destroy()
    
    def get_user_input_for_connection(self):
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        
        # Get IP address
        self.SERVER_IP = simpledialog.askstring(
            "Server IP", 
            "Enter the server IP address:",
            initialvalue="127.0.0.1"
        )
        if not self.SERVER_IP:
            self.SERVER_IP = "127.0.0.1"  # Default if canceled
            
        # Get port
        port_str = simpledialog.askstring(
            "Server Port", 
            "Enter the server port number:",
            initialvalue="5000"
        )
        try:
            self.SERVER_PORT = int(port_str) if port_str else 5000
        except ValueError:
            messagebox.showwarning("Invalid Port", "Invalid port number. Using default port 5000.")
            self.SERVER_PORT = 5000
            
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
    # Create client
    client = MorseClient()
    
    # Application setup
    root = tk.Tk()
    root.title("Morse Code Client")
    
    # Set app icon (optional)
    try:
        root.iconbitmap("morse_icon.ico")  # You can add an icon file
    except:
        pass  # Ignore if icon file doesn't exist
    
    # Try to connect
    if client.connect():
        # Create GUI and show connection details
        app = MorseGUI(root, client)
        messagebox.showinfo("Connection Successful", 
                           f"Connected to server at {client.SERVER_IP}:{client.SERVER_PORT}")
        
        # Set close handler
        def on_closing():
            if messagebox.askokcancel("Quit", "Do you want to quit the application?"):
                client.close()
                root.quit()
                root.destroy()
                
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        # Start GUI main loop
        root.mainloop()
    else:
        messagebox.showerror("Connection Error", 
                           f"Failed to connect to server at {client.SERVER_IP}:{client.SERVER_PORT}\n\n{client.connection_status}")
        root.destroy()