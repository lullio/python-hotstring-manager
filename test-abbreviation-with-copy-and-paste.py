import keyboard
import pyperclip

def setup_large_abbreviation():
    # Define uma abreviação que substitui "html" por um código HTML grande
    large_html_code = """<html>
<head>
    <title>Example</title>
</head>
<body>
    <h1>This is a heading</h1>
    <p>This is a paragraph.</p>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
    </ul>
</body>
</html>"""

    def insert_large_html():
        # Copiar o código HTML para o clipboard
        pyperclip.copy(large_html_code)
        # Colar o conteúdo do clipboard
        keyboard.press_and_release('ctrl+v')

    # Configurar a hotkey para chamar a função insert_large_html quando 'html' for digitado
    keyboard.add_word_listener("html", insert_large_html, triggers=['space', 'enter'], match_suffix=True)

    print("Abbreviation set for 'html'. Type 'html' followed by a space or enter to see the replacement.")

if __name__ == "__main__":
    setup_large_abbreviation()
    print("Listening for abbreviations... (Press 'esc' to exit)")
    keyboard.wait("esc")  # Use a tecla 'esc' para terminar o script
