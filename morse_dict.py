MORSE_CODE_DICT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F', '--.': 'G',
    '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N',
    '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T', '..-': 'U',
    '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y', '--..': 'Z', '-----': '0', '.----': '1',
    '..---': '2', '...--': '3', '....-': '4', '.....': '5', '-....': '6', '--...': '7',
    '---..': '8', '----.': '9', '.-.-.-': '.', '--..--': ',', '..--..': '?', '-.-.--': '!',
    '-..-.': '/', '.-.-.': '+', '-....-': '-', '.----.': "'", '-.--.': '(', '-.--.-': ')',
    '/': ' ', '...---...' : 'SOS'
}

def morse_to_text(morse_code):
    words = morse_code.strip().split(' / ')  # Split by space ('/') for character separation
    translated_message = []
    for word in words:
        letters = word.split(' ')
        translated_word = ''.join([MORSE_CODE_DICT.get(letter, '_') for letter in letters])
        translated_message.append(translated_word)
    return ' '.join(translated_message)