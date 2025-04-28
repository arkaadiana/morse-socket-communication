import tkinter as tk
import socket
import time
import threading
import winsound
from pynput.mouse import Listener
import keyboard
import os
from dotenv import load_dotenv
from morse_dict import morse_to_text

load_dotenv()


# Initialize global variables
morse_code = ""
start_time = 0
is_mouse_pressed = False
SERVER_IP = os.getenv("SERVER_IP")
SERVER_PORT = int(os.getenv("SERVER_PORT"))

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP , SERVER_PORT))


# Function to play Morse code sound
def play_morse_sound(symbol):
    if symbol == '.':
        winsound.Beep(1000, 200)
    elif symbol == '-':
        winsound.Beep(1000, 600)
    else:
        time.sleep(0.2)


def get_client_ip():  # A random address just to get the active interface
    client_ip = client_socket.getsockname()[0]
    return client_ip

client_ip = get_client_ip()


# Function to handle mouse click input for Morse Code
def on_click(x, y, button, pressed):
    global start_time, morse_code, is_mouse_pressed

    if button.name == 'left':
        if pressed:
            start_time = time.time()
            draw_mouse_area("green")
        else:
            press_duration = time.time() - start_time
            if press_duration < 0.2:
                morse_code += '.'
                play_morse_sound('.')
            else:
                morse_code += '-'
                play_morse_sound('-')
            start_time = 0 
            draw_mouse_area("khaki")
            update_gui()
    elif button.name == 'right':
        if morse_code and not morse_code.strip().endswith('/'):
            morse_code += ' / '
        update_gui()


# Function to draw the mouse area with a circle (no image)
def draw_mouse_area(color):
    canvas.delete("all")
    canvas.create_oval(50, 50, 250, 250, fill=color, outline="black", width=3)


# Function to start mouse listener
def start_mouse_listener():
    with Listener(on_click=on_click) as listener:
        listener.join()


# Function to update GUI with the current Morse code and translation
def update_gui():
    morse_label.config(text=f"Morse Code: {morse_code}")
    translated_message = morse_to_text(morse_code)
    translation_label.config(text=f"Translated: {translated_message}")


# Function to send the message to the server
def capture_space_key():
    global morse_code
    if keyboard.is_pressed('space'):
        if morse_code:
            send_message(morse_code, client_ip)
            morse_code = "" 
            update_gui()


# Function to send the message to the server
def send_message(morse_code, client_ip):
    message = f"{morse_code}"
    client_socket.send(message.encode('utf-8'))


# GUI Setup
root = tk.Tk()
root.title("Morse Code Translator")
root.geometry("500x500")

# Set the background color and font
root.configure(bg='khaki')

# Labels for Morse code and translation
morse_label = tk.Label(root, text="Morse Code: ", font=("Courier New", 16), fg="black", bg="khaki", padx=20, pady=10)
morse_label.pack(pady=10)

translation_label = tk.Label(root, text="Translated: ", font=("Courier New", 16), fg="black", bg="khaki", padx=20, pady=10)
translation_label.pack(pady=10)

# Create a Canvas widget
canvas = tk.Canvas(root, width=300, height=300, bg="khaki", bd=5, relief="solid")
canvas.pack(pady=30)

# Start the listener in a separate thread
threading.Thread(target=start_mouse_listener, daemon=True).start()

# Continuously check for space key to send Morse code
def check_for_space():
    while True:
        capture_space_key()
        time.sleep(0.1)

# Start the space key checking thread
threading.Thread(target=check_for_space, daemon=True).start()

# Start the Tkinter main loop
root.mainloop()
