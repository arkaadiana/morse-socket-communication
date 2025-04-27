import tkinter as tk
import socket
import time
import threading
import winsound
from pynput.mouse import Listener
import keyboard

# Morse Code Dictionary
MORSE_CODE_DICT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G',
    '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N',
    '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T', '..-': 'U',
    '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y', '--..': 'Z', '-----': '0', '.----': '1',
    '..---': '2', '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7',
    '---..': '8', '----.': '9', '.-.-.-': '.', '--..--': ',', '..--..': '?', '-.-.--': '!',
    '-..-.': '/', '.-.-.': '+', '-....-': '-', '.----.': "'", '-.--.': '(', '-.--.-': ')',
    '/': ' '  # Space separator in Morse code
}

# Function to play Morse code sound
def play_morse_sound(symbol):
    if symbol == '.':
        winsound.Beep(1000, 200)
    elif symbol == '-':
        winsound.Beep(1000, 600)
    else:
        time.sleep(0.2)

# Morse to Text Conversion
def morse_to_text(morse_code):
    words = morse_code.strip().split(' / ')  # Split by space ('/') for word separation
    translated_message = []
    for word in words:
        letters = word.split(' ')
        translated_word = ''.join([MORSE_CODE_DICT.get(letter, '') for letter in letters])
        translated_message.append(translated_word)
    return ' '.join(translated_message)

# Initialize global variables
morse_code = ""
start_time = 0
is_mouse_pressed = False

# Function to handle mouse click input for Morse Code
def on_click(x, y, button, pressed):
    global start_time, morse_code, is_mouse_pressed

    if button.name == 'left':  # Left mouse button
        if pressed:
            start_time = time.time()  # Start counting when mouse button is pressed
            draw_mouse_area("green")  # Change color to indicate press
        else:
            press_duration = time.time() - start_time
            if press_duration < 0.2:
                morse_code += '.'
                play_morse_sound('.')  # Play dot sound
            else:
                morse_code += '-'
                play_morse_sound('-')  # Play dash sound
            start_time = 0  # Reset the timer after the click is released
            draw_mouse_area("khaki")  # Reset background color
            update_gui()

# Function to draw the mouse area with a circle (no image)
def draw_mouse_area(color):
    canvas.delete("all")  # Clear the canvas
    # Draw a circle that changes color based on mouse press
    canvas.create_oval(50, 50, 250, 250, fill=color, outline="black", width=3)  # Circle for visual effect

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
def send_message(morse_code):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('192.168.18.7', 5555))  # Update server IP
    client_socket.send(morse_code.encode('utf-8'))
    client_socket.close()

# Function to capture space key press (send Morse code)
def capture_space_key():
    global morse_code
    if keyboard.is_pressed('space'):  # Space bar for sending the code
        send_message(morse_code)
        morse_code = ""  # Reset the code
        update_gui()

# GUI Setup
root = tk.Tk()
root.title("Morse Code Translator")
root.geometry("500x500")  # Adjusted size to accommodate all elements

# Set the background color and font to fit the theme
root.configure(bg='khaki')

# Labels for Morse code and translation
morse_label = tk.Label(root, text="Morse Code: ", font=("Courier New", 16), fg="black", bg="khaki", padx=20, pady=10)
morse_label.pack(pady=10)

translation_label = tk.Label(root, text="Translated: ", font=("Courier New", 16), fg="black", bg="khaki", padx=20, pady=10)
translation_label.pack(pady=10)

# Create a Canvas widget to draw the mouse-like area (no image)
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
