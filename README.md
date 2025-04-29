# Morse Code Socket Communication System

This project implements a simple Morse Code communication system with a client-server model. The server listens for incoming connections from clients, which send Morse code messages. The server then translates these messages into text and broadcasts the translated text back to the clients.

## Overview

This system consists of the following components:

- **Server ([`server.py`](server.py))**: Handles incoming client connections, processes received Morse code messages, and broadcasts translated text.
- **Client ([`client.py`](client.py))**: Allows users to input Morse code using their mouse and keyboard and sends it to the server for translation.
- **Graphical User Interface ([`gui.py`](gui.py))**: Built using Tkinter, provides an interactive interface for sending and receiving Morse code messages.
- **Morse Code Dictionary ([`morse_dict.py`](morse_dict.py))**: Maps Morse code symbols to letters and numbers and includes a translation function.


## Requirements

- Python 3.x
- Dependencies:
  ```
  python-dotenv  # For loading environment variables
  keyboard       # For capturing keyboard input
  pynput         # For capturing mouse events
  winsound       # For playing Morse code sounds
  ```

## Installation

Install the required dependencies:

```bash
pip install python-dotenv pynput keyboard
```
Alternatively, you can use the following command to install dependencies from [`requirements.txt`](requirements.txt):

```bash
pip install -r requirements.txt
```

## Setup

### Server Setup
The server listens on a specified IP address and port, and clients can connect to it. The server can be started as follows:

1. **Run the server**:
    - The .env file will be automatically created the first time the server is run if it doesn't already exist. The file will contain the default values for SERVER_IP and SERVER_PORT. If these values are missing or incorrect, they will be updated automatically.

    - The server can be started by running:

        ```bash
        python server.py
        ```
    - The server will listen for incoming client connections on the IP and port specified in the .env file (or the default values if the .env file is created). If the .env file does not exist, the server will create it and set default values (127.0.0.1 for IP and 5555 for port).

2. **.env File**:  
    - The .env file will automatically be created with the following content if it does not exist:
        ```
        SERVER_IP=127.0.0.1
        SERVER_PORT=5555
        ```

### Client Setup
The client application allows users to interact with the server and send Morse code. It uses a graphical interface where users can click and hold the mouse to input dots and dashes for Morse code, and it will also send the input to the server.

1. **Configure `.env` file**:  
    - The client will automatically load connection details from the .env file. If the details are not found, it will prompt the user for input (IP and port).

2. **Run the client**:
    - Run the client by executing:
        ```bash
        python client.py
        ```
    The client will attempt to connect to the server and, once connected, will allow the user to input Morse code and send messages.


## File Breakdown

### 1. [`server.py`](server.py)
* **Main Functionality**:
   * Listens for incoming client connections.
   * Receives Morse code from clients, translates it to text, and broadcasts it to all other connected clients.
   * Handles the shutdown of the server when the ESC key is pressed.
* **Key Functions**:
   * `get_server_ip()`: Gets the local IP address of the server.
   * `ensure_env_updated()`: Creates or updates the `.env` file with server IP and port.
   * `client_handler()`: Handles communication with each client.
   * `broadcast()`: Sends a message to all clients except the sender.
   * `listen_for_shutdown()`: Listens for the ESC key to shut down the server.
   * `start_server()`: Starts the server and listens for client connections.

### 2. [`client.py`](client.py)
* **Main Functionality**:
   * Connects to the server based on configuration from the `.env` file or user input.
   * Allows users to input Morse code using the mouse (left-click for dot, long press for dash).
   * Displays the translated message received from the server in the GUI.
   * Sends the input Morse code to the server for translation.
* **Key Functions**:
   * `get_connection_details()`: Loads or prompts for server connection details (IP and port).
   * `connect()`: Connects to the server using the specified IP and port.
   * `send_message()`: Sends Morse code to the server.
   * `close()`: Closes the socket connection.

### 3. [`gui.py`](gui.py)
* **Main Functionality**:
   * Provides the graphical interface for the user to input Morse code using the mouse.
   * Displays the current Morse code input and its translated message.
   * Provides visual feedback when recording Morse code (dots and dashes).
* **Key Functions**:
   * `setup_gui()`: Sets up the GUI layout, including labels, buttons, and canvas.
   * `display_dictionary()`: Displays a dictionary of Morse code symbols and their corresponding letters and numbers.
   * `on_click()`: Handles mouse click events to record dots and dashes.
   * `process_queue()`: Processes events from a queue to update the GUI.
   * `check_for_space()`: Listens for the spacebar to trigger sending the Morse code to the server.

### 4. [`morse_dict.py`](morse_dict.py)
* **Main Functionality**:
   * Contains the Morse code dictionary that maps Morse code symbols to letters, numbers, and special characters.
   * Provides a function `morse_to_text()` to convert a string of Morse code into readable text.

## Usage

### 1. **Run the Server**:
   * First, start the server by running `python server.py` on the machine you want to act as the server. The `.env` file will be created if it doesn't exist.

### 2. **Run the Client**:
   * Run `python client.py` on the client machine. The client will ask for the server IP and port if not already specified in the `.env` file. Once connected, you can start inputting Morse code using the mouse or keyboard.

### 3. **Interaction**:
   * Left-click and hold to input a dot (short press) or dash (long press).
   * Right-click to add a word separator (`/`).
   * Press the spacebar to send the message to the server.

## Notes
* The **ESC key** can be used to shut down the server.
* The **Morse code dictionary** contains standard Morse code symbols for letters, numbers, and special characters, including a special entry for SOS (`...---...`).
* The **server** broadcasts all received Morse code messages (translated into text) to all connected clients except the sender.
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.