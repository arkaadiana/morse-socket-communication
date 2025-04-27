import socket
import threading

clients = []

# Morse code translation table
MORSE_CODE_DICT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G',
    '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N',
    '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T', '..-': 'U',
    '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y', '--..': 'Z', '-----': '0', '.----': '1',
    '..---': '2', '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7',
    '---..': '8', '----.': '9', '.-.-.-': '.', '--..--': ',', '..--..': '?', '-.-.--': '!',
    '-..-.': '/', '.-.-.': '+', '-....-': '-', '.----.': "'", '-.--.': '(', '-.--.-': ')',
    '/': ' ',  # Space separator in Morse code
}

# Function to translate Morse code into text
def morse_to_text(morse_code):
    words = morse_code.strip().split(' / ')  # Split by space ('/') for word separation
    translated_message = []
    for word in words:
        letters = word.split(' ')
        translated_word = ''.join([MORSE_CODE_DICT.get(letter, '') for letter in letters])
        translated_message.append(translated_word)
    return ' '.join(translated_message)

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

# Run the server
if __name__ == "__main__":
    start_server("192.168.18.7", 5555)
