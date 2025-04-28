import socket
import threading
import os
import keyboard
from dotenv import load_dotenv
from morse_dict import morse_to_text

load_dotenv()

clients = []


def get_server_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def generate_env(env_path='.env', server_ip='127.0.0.1', default_port='5555'):
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            lines = f.readlines()
        
        keys_in_file = [line.split('=')[0].strip() for line in lines if '=' in line]
        
        if 'SERVER_IP' not in keys_in_file:
            with open(env_path, 'a') as f:
                f.write(f'\nSERVER_IP={server_ip}')
    else:
        # .env does not exist, create it
        with open(env_path, 'w') as f:
            f.write(f'PORT={default_port}\n')
            f.write(f'SERVER_IP={server_ip}')


# Handle communication with each client
def client_handler(client_socket, client_address):
    print(f"[NEW CONNECTION] {client_address} connected.")
    while True:
        try:
            # Receive message from client
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"[{client_address}] Morse Code Message Received: {message}")
                translated_message = morse_to_text(message)
                print(f"[{client_address}] Translated Message: {translated_message}")
                # Broadcast the translated message to other clients
                broadcast(client_socket, translated_message)
            else:
                break
        except:
            break

    # Remove the client from the list and close the connection
    print(f"[{client_address}] Disconnected.")
    clients.remove(client_socket)
    client_socket.close()


# Broadcast a message to all other clients
def broadcast(sender_socket, message):
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except:
                continue


# Function to stop the server gracefully when ESC key is pressed
def listen_for_shutdown():
    print("[INFO] Press ESC to stop the server.")
    while True:
        if keyboard.is_pressed('esc'):  # If ESC key is pressed
            print("[INFO] ESC key pressed. Shutting down the server...")
            os._exit(0)


# Start the server
def start_server(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"[LISTENING] Server is listening on {host}:{port}")
    while True:
        client_socket, client_address = server_socket.accept()
        clients.append(client_socket)
        client_thread = threading.Thread(target=client_handler, args=(client_socket, client_address))
        client_thread.start()


server_ip = get_server_ip()
generate_env(server_ip=server_ip)
SERVER_PORT = int(os.getenv("SERVER_PORT"))

# Start the shutdown listener thread
shutdown_thread = threading.Thread(target=listen_for_shutdown, daemon=True)
shutdown_thread.start()

# Run the server
if __name__ == "__main__":
    start_server(server_ip, SERVER_PORT)
