import socket
import threading
import os
import keyboard
from dotenv import load_dotenv, dotenv_values, set_key
from morse_dict import morse_to_text

ENV_PATH = '.env'
clients = []


def get_server_ip():
    """Get local IP address."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def ensure_env_updated(env_path=ENV_PATH, server_ip='127.0.0.1', default_port='5555'):
    """
    Create or update .env file:
    - Create if not exists.
    - Update SERVER_IP if different from current IP.
    - Add SERVER_PORT if missing.
    """
    # Load existing .env or create default
    env_vars = {}
    if os.path.exists(env_path):
        env_vars = dotenv_values(env_path)
    else:
        with open(env_path, 'w') as f:
            f.write(f"SERVER_PORT={default_port}\nSERVER_IP={server_ip}\n")
        print("[INFO] .env file created with default values.")
        return

    # Update SERVER_IP if different
    current_ip = env_vars.get("SERVER_IP")
    if current_ip != server_ip:
        print(f"[INFO] SERVER_IP in .env is outdated ({current_ip}), updating to {server_ip}")
        set_key(env_path, "SERVER_IP", server_ip)

    # Add default SERVER_PORT if missing
    if "SERVER_PORT" not in env_vars:
        print(f"[INFO] SERVER_PORT missing in .env, setting default to {default_port}")
        set_key(env_path, "SERVER_PORT", default_port)


def client_handler(client_socket, client_address):
    """Handle communication with each client."""
    print(f"[NEW CONNECTION] {client_address} connected.")
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"[{client_address}] Morse Code Message Received: {message}")
                translated_message = morse_to_text(message)
                print(f"[{client_address}] Translated Message: {translated_message}")
                broadcast(client_socket, translated_message)
            else:
                break
        except Exception as e:
            print(f"[ERROR] Error handling client {client_address}: {e}")
            break

    print(f"[{client_address}] Disconnected.")
    if client_socket in clients:
        clients.remove(client_socket)
    client_socket.close()


def broadcast(sender_socket, message):
    """Broadcast a message to all clients except sender."""
    for client in clients:
        if client != sender_socket:
            try:
                client.send(message.encode('utf-8'))
            except Exception:
                continue


def listen_for_shutdown():
    """Listen for ESC key press to shutdown server."""
    print("[INFO] Press ESC to stop the server.")
    while True:
        if keyboard.is_pressed('esc'):
            print("[INFO] ESC key pressed. Shutting down the server...")
            os._exit(0)


def start_server(host, port):
    """Start the socket server."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"[LISTENING] Server is listening on {host}:{port}")
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            clients.append(client_socket)
            client_thread = threading.Thread(target=client_handler, args=(client_socket, client_address))
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[INFO] KeyboardInterrupt received. Shutting down the server...")
    finally:
        server_socket.close()
        for client in clients:
            client.close()
        print("[INFO] Server shutdown complete.")


if __name__ == "__main__":
    server_ip = get_server_ip()
    ensure_env_updated(server_ip=server_ip)
    load_dotenv()  # Load updated env values

    port = os.getenv("SERVER_PORT")
    if port is None:
        raise ValueError("SERVER_PORT not found in environment variables.")
    SERVER_PORT = int(port)

    # Start shutdown listener in a separate thread
    shutdown_thread = threading.Thread(target=listen_for_shutdown, daemon=True)
    shutdown_thread.start()

    # Start the server
    start_server(server_ip, SERVER_PORT)
