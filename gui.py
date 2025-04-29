import tkinter as tk
from tkinter import ttk, font
import time
import threading
import winsound
from pynput.mouse import Listener
import keyboard
from morse_dict import MORSE_CODE_DICT, morse_to_text
import queue

class MorseGUI:
    def __init__(self, root, client=None):
        self.root = root
        self.morse_code = ""
        self.start_time = 0
        self.is_mouse_pressed = False
        
        # Use the provided client if available
        self.client = client
        
        # Create a queue for thread-safe communication
        self.event_queue = queue.Queue()
        
        # Apply modern style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Colors
        self.bg_color = "#f0f0f0"
        self.primary_color = "#3498db"
        self.secondary_color = "#2ecc71"
        self.accent_color = "#e74c3c"
        self.text_color = "#2c3e50"
        
        # Configure GUI
        self.setup_gui()
        
        # Start threads
        self.mouse_thread = threading.Thread(target=self.start_mouse_listener, daemon=True)
        self.mouse_thread.start()
        
        self.keyboard_thread = threading.Thread(target=self.check_for_space, daemon=True)
        self.keyboard_thread.start()
        
        # Start periodic checking of the queue (thread-safe UI updates)
        self.root.after(100, self.process_queue)
        
    def setup_gui(self):
        # Set the window properties
        self.root.title("Morse Code Translator")
        self.root.geometry("800x600")
        self.root.configure(bg=self.bg_color)
        self.root.resizable(True, True)
        
        # Custom fonts
        title_font = font.Font(family="Helvetica", size=18, weight="bold")
        header_font = font.Font(family="Helvetica", size=14, weight="bold")
        normal_font = font.Font(family="Helvetica", size=12)
        dict_font = font.Font(family="Courier", size=10)
        
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.bg_color)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title and server info
        title_frame = tk.Frame(main_frame, bg=self.bg_color)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(title_frame, 
                              text="Morse Code Translator", 
                              font=title_font, 
                              fg=self.primary_color, 
                              bg=self.bg_color)
        title_label.pack(side=tk.LEFT)
        
        # Server info - only show if client is provided
        if self.client:
            server_frame = tk.Frame(title_frame, bg=self.bg_color)
            server_frame.pack(side=tk.RIGHT)
            
            server_info = f"Server: {self.client.SERVER_IP}:{self.client.SERVER_PORT}"
            server_label = tk.Label(server_frame, 
                                   text=server_info, 
                                   font=normal_font, 
                                   fg=self.text_color, 
                                   bg=self.bg_color)
            server_label.pack(side=tk.TOP)
            
            client_info = f"Client IP: {self.client.client_ip}"
            client_label = tk.Label(server_frame, 
                                  text=client_info, 
                                  font=normal_font, 
                                  fg=self.text_color, 
                                  bg=self.bg_color)
            client_label.pack(side=tk.TOP)
        
        # Left panel - Interactive area
        left_panel = tk.Frame(main_frame, bg=self.bg_color)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Input area
        input_frame = tk.LabelFrame(left_panel, 
                                   text="Morse Code Input", 
                                   font=header_font, 
                                   fg=self.text_color, 
                                   bg=self.bg_color)
        input_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Canvas for visual feedback
        self.canvas = tk.Canvas(input_frame, 
                              width=300, height=200, 
                              bg=self.bg_color, 
                              bd=2, 
                              relief="ridge")
        self.canvas.pack(pady=20, padx=20)
        
        # Draw initial circle
        self.draw_mouse_area(self.bg_color)
        
        # Instructions
        instructions_text = """
        Instructions:
        • Left-click: Short press (dot), Long press (dash)
        • Right-click: Add word separator (/)
        • Space key: Send message
        """
        instructions_label = tk.Label(input_frame, 
                                    text=instructions_text, 
                                    font=normal_font, 
                                    fg=self.text_color, 
                                    bg=self.bg_color, 
                                    justify=tk.LEFT)
        instructions_label.pack(pady=10, padx=20, anchor=tk.W)
        
        # Current input
        input_display_frame = tk.Frame(left_panel, bg=self.bg_color)
        input_display_frame.pack(fill=tk.X, pady=10)
        
        self.morse_label = tk.Label(input_display_frame, 
                                  text="Morse Code: ", 
                                  font=normal_font,
                                  fg=self.text_color, 
                                  bg=self.bg_color,
                                  anchor=tk.W)
        self.morse_label.pack(fill=tk.X)
        
        self.translation_label = tk.Label(input_display_frame, 
                                        text="Translated: ", 
                                        font=normal_font, 
                                        fg=self.primary_color, 
                                        bg=self.bg_color,
                                        anchor=tk.W)
        self.translation_label.pack(fill=tk.X)
        
        # Clear button
        self.clear_button = tk.Button(input_display_frame, 
                                    text="Clear", 
                                    command=self.clear_morse,
                                    font=normal_font,
                                    bg=self.accent_color,
                                    fg="white",
                                    padx=10)
        self.clear_button.pack(pady=10)
        
        # Right panel - Dictionary (Replacing Message History)
        right_panel = tk.Frame(main_frame, bg=self.bg_color)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        # Dictionary display
        dict_frame = tk.LabelFrame(right_panel, 
                                text="Morse Code Dictionary", 
                                font=header_font, 
                                fg=self.text_color, 
                                bg=self.bg_color)
        dict_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create a frame for the dictionary content with scrollbar
        dict_content_frame = tk.Frame(dict_frame, bg="white")
        dict_content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create a canvas for scrolling
        dict_canvas = tk.Canvas(dict_content_frame, bg="white")
        scrollbar = tk.Scrollbar(dict_content_frame, orient="vertical", command=dict_canvas.yview)
        
        # Configure the canvas
        dict_canvas.configure(yscrollcommand=scrollbar.set)
        dict_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create a frame inside the canvas to hold the dictionary entries
        self.dict_inner_frame = tk.Frame(dict_canvas, bg="white")
        dict_canvas.create_window((0, 0), window=self.dict_inner_frame, anchor="nw")
        
        # Display the dictionary in multi-column format
        self.display_dictionary()
        
        # Configure the canvas to adjust the scroll region when dictionary frame changes size
        self.dict_inner_frame.update_idletasks()
        dict_canvas.config(scrollregion=dict_canvas.bbox("all"))
        
        # Status bar
        status_frame = tk.Frame(self.root, bg=self.primary_color, height=25)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.status_label = tk.Label(status_frame, 
                                   text="Ready", 
                                   fg="white", 
                                   bg=self.primary_color, 
                                   anchor=tk.W, 
                                   padx=10)
        self.status_label.pack(side=tk.LEFT, fill=tk.X)

    def display_dictionary(self):
        # Invert the dictionary to sort by characters (A-Z, 0-9, symbols)
        inverted_dict = {}
        for morse, char in MORSE_CODE_DICT.items():
            inverted_dict[char] = morse
            
        # Sort the keys alphabetically
        sorted_chars = sorted(inverted_dict.keys())
        
        # Group into letters (A-Z), numbers (0-9), and symbols
        letters = [c for c in sorted_chars if c.isalpha()]
        numbers = [c for c in sorted_chars if c.isdigit()]
        symbols = [c for c in sorted_chars if not c.isalnum() and c != ' ']
        space = [' '] if ' ' in sorted_chars else []
        
        # Special case for SOS
        special = ['SOS'] if 'SOS' in sorted_chars else []
        
        # Create column headings
        heading_font = font.Font(family="Helvetica", size=10, weight="bold")
        dict_font = font.Font(family="Courier", size=10)
        
        # Determine number of columns and items per column for letters
        num_columns = 3
        letters_per_column = -(-len(letters) // num_columns)  # Ceiling division
        
        # Create frames for each section
        letters_frame = tk.LabelFrame(self.dict_inner_frame, 
                                     text="Letters (A-Z)", 
                                     font=heading_font,
                                     fg=self.text_color,
                                     bg="white")
        letters_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create columns for letters
        letter_columns = []
        for i in range(num_columns):
            col_frame = tk.Frame(letters_frame, bg="white")
            col_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            letter_columns.append(col_frame)
        
        # Fill the columns with letters
        for i, char in enumerate(letters):
            col_idx = i // letters_per_column
            if col_idx < len(letter_columns):
                entry_frame = tk.Frame(letter_columns[col_idx], bg="white")
                entry_frame.pack(anchor=tk.W, pady=2)
                
                char_label = tk.Label(entry_frame, 
                                    text=f"{char}: ", 
                                    font=dict_font, 
                                    width=3,
                                    fg=self.text_color, 
                                    bg="white")
                char_label.pack(side=tk.LEFT)
                
                morse_label = tk.Label(entry_frame, 
                                     text=inverted_dict[char], 
                                     font=dict_font,
                                     fg=self.primary_color, 
                                     bg="white")
                morse_label.pack(side=tk.LEFT)
        
        # Numbers and symbols section
        other_frame = tk.LabelFrame(self.dict_inner_frame, 
                                  text="Numbers & Symbols", 
                                  font=heading_font,
                                  fg=self.text_color,
                                  bg="white")
        other_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Two columns for numbers and symbols
        numbers_frame = tk.Frame(other_frame, bg="white")
        numbers_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        symbols_frame = tk.Frame(other_frame, bg="white")
        symbols_frame.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        
        # Display numbers
        for char in numbers:
            entry_frame = tk.Frame(numbers_frame, bg="white")
            entry_frame.pack(anchor=tk.W, pady=2)
            
            char_label = tk.Label(entry_frame, 
                                text=f"{char}: ", 
                                font=dict_font, 
                                width=3,
                                fg=self.text_color, 
                                bg="white")
            char_label.pack(side=tk.LEFT)
            
            morse_label = tk.Label(entry_frame, 
                                 text=inverted_dict[char], 
                                 font=dict_font,
                                 fg=self.primary_color, 
                                 bg="white")
            morse_label.pack(side=tk.LEFT)
        
        # Display symbols
        for char in symbols + space:
            entry_frame = tk.Frame(symbols_frame, bg="white")
            entry_frame.pack(anchor=tk.W, pady=2)
            
            # For space, show a visual representation
            display_char = "Space" if char == " " else char
            
            char_label = tk.Label(entry_frame, 
                                text=f"{display_char}: ", 
                                font=dict_font, 
                                width=6,
                                fg=self.text_color, 
                                bg="white")
            char_label.pack(side=tk.LEFT)
            
            morse_label = tk.Label(entry_frame, 
                                 text=inverted_dict[char], 
                                 font=dict_font,
                                 fg=self.primary_color, 
                                 bg="white")
            morse_label.pack(side=tk.LEFT)
        
        # Special codes (if any)
        if special:
            special_frame = tk.LabelFrame(self.dict_inner_frame, 
                                        text="Special Codes", 
                                        font=heading_font,
                                        fg=self.text_color,
                                        bg="white")
            special_frame.pack(fill=tk.X, padx=5, pady=5)
            
            for char in special:
                entry_frame = tk.Frame(special_frame, bg="white")
                entry_frame.pack(anchor=tk.W, pady=2)
                
                char_label = tk.Label(entry_frame, 
                                    text=f"{char}: ", 
                                    font=dict_font, 
                                    width=6,
                                    fg=self.text_color, 
                                    bg="white")
                char_label.pack(side=tk.LEFT)
                
                morse_label = tk.Label(entry_frame, 
                                     text=inverted_dict[char], 
                                     font=dict_font,
                                     fg=self.primary_color, 
                                     bg="white")
                morse_label.pack(side=tk.LEFT)
    
    def process_queue(self):
        """Process UI update events from the queue"""
        try:
            while True:
                # Get event from queue without blocking
                event = self.event_queue.get_nowait()
                
                # Process the event based on its type
                event_type = event.get('type')
                
                if event_type == 'mouse_down':
                    self.draw_mouse_area(self.secondary_color)
                    self.status_label.config(text="Recording dot/dash...")
                
                elif event_type == 'mouse_up':
                    symbol = event.get('symbol')
                    self.morse_code += symbol
                    self.play_morse_sound(symbol)
                    self.status_label.config(text=f"Recorded {symbol}")
                    self.draw_mouse_area(self.bg_color)
                    self.update_gui()
                
                elif event_type == 'word_separator':
                    self.morse_code += ' / '
                    self.status_label.config(text="Added word separator")
                    self.update_gui()
                
                elif event_type == 'send_message':
                    self.send_message()
                
                elif event_type == 'set_status':
                    self.status_label.config(text=event.get('text', ''))
                
                # Mark this task as done
                self.event_queue.task_done()
                
        except queue.Empty:
            # Queue is empty, schedule the next check
            pass
        
        # Schedule the next queue check
        self.root.after(100, self.process_queue)
            
    def on_click(self, x, y, button, pressed):
        try:
            if button.name == 'left':
                if pressed:
                    self.start_time = time.time()
                    # Queue UI update instead of direct call
                    self.event_queue.put({'type': 'mouse_down'})
                    
                else:
                    press_duration = time.time() - self.start_time
                    symbol = '.' if press_duration < 0.2 else '-'
                    # Queue UI update instead of direct call
                    self.event_queue.put({'type': 'mouse_up', 'symbol': symbol})
                    self.start_time = 0
                    
            elif button.name == 'right' and not pressed:
                if self.morse_code and not self.morse_code.strip().endswith('/'):
                    # Queue UI update instead of direct call
                    self.event_queue.put({'type': 'word_separator'})
        except Exception as e:
            print(f"Error in on_click: {e}")
            
    def play_morse_sound(self, symbol):
        try:
            if symbol == '.':
                winsound.Beep(1000, 200)
            elif symbol == '-':
                winsound.Beep(1000, 600)
            else:
                time.sleep(0.2)
        except Exception as e:
            print(f"Sound error: {e}")
            
    def draw_mouse_area(self, color):
        self.canvas.delete("all")
        # Draw circle
        self.canvas.create_oval(50, 20, 250, 180, fill=color, outline=self.primary_color, width=3)
        # Add text
        if color == self.secondary_color:
            text = "Recording..."
        else:
            text = "Click and hold for input"
        self.canvas.create_text(150, 100, text=text, fill=self.text_color, font=("Helvetica", 12, "bold"))
        
    def start_mouse_listener(self):
        try:
            with Listener(on_click=self.on_click) as listener:
                listener.join()
        except Exception as e:
            print(f"Mouse listener error: {e}")
            self.event_queue.put({'type': 'set_status', 'text': f"Mouse listener error: {e}"})
            
    def update_gui(self):
        # Update morse code display
        if self.morse_code:
            self.morse_label.config(text=f"Morse Code: {self.morse_code}")
        else:
            self.morse_label.config(text="Morse Code: ")
            
        # Update translation
        translated_message = morse_to_text(self.morse_code)
        if translated_message:
            self.translation_label.config(text=f"Translated: {translated_message}")
        else:
            self.translation_label.config(text="Translated: ")
            
    def clear_morse(self):
        self.morse_code = ""
        self.update_gui()
        self.status_label.config(text="Input cleared")
        
    def check_for_space(self):
        try:
            while True:
                if keyboard.is_pressed('space'):
                    if self.morse_code:
                        # Queue the send message event instead of direct call
                        self.event_queue.put({'type': 'send_message'})
                        # Small delay to avoid multiple triggers
                        time.sleep(0.3)
                    else:
                        time.sleep(0.1)
                else:
                    time.sleep(0.1)
        except Exception as e:
            print(f"Keyboard listener error: {e}")
            self.event_queue.put({'type': 'set_status', 'text': f"Keyboard listener error: {e}"})
            
    def send_message(self):
        if not self.morse_code:
            return
            
        translated = morse_to_text(self.morse_code)
        
        # Send to server if client is available
        if self.client:
            success = self.client.send_message(self.morse_code)
            
            if success:
                self.status_label.config(text=f"Sent: {translated}")
            else:
                self.status_label.config(text="Failed to send message")
        else:
            self.status_label.config(text=f"Translated: {translated}")
            
        # Clear input
        self.morse_code = ""
        self.update_gui()

# Main application entry point
if __name__ == "__main__":
    root = tk.Tk()
    app = MorseGUI(root)
    root.mainloop()