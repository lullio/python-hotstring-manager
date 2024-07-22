import keyboard

def test_hotstrings():
    # Define uma hotstring simples
    keyboard.add_abbreviation("test", "Hotstring Triggered!")

    print("Listening for hotstrings... (Press 'esc' to exit)")
    keyboard.wait("esc")  # Use a tecla 'esc' para terminar o script

if __name__ == "__main__":
    test_hotstrings() 