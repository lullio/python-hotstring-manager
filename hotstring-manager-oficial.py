import json
import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import threading

CONFIG_FILE = "hotstrings.json"

class HotstringManager:
    def __init__(self, master):
        self.master = master
        self.master.title("Gerenciador de Hotstrings")

        # Carregar hotstrings do arquivo de configuração
        self.hotstrings = self.load_hotstrings()

        # Configurar escuta de hotstrings
        self.setup_hotstring_listener()

        # Widgets da interface
        self.create_widgets()

        # Iniciar o monitoramento de teclado em um thread separado
        self.keyboard_thread = threading.Thread(target=self.start_keyboard_listener, daemon=True)
        self.keyboard_thread.start()

    def load_hotstrings(self):
        try:
            with open(CONFIG_FILE, "r") as file:
                data = json.load(file)
                return data["hotstrings"]
        except FileNotFoundError:
            return []

    def save_hotstrings(self):
        data = {"hotstrings": self.hotstrings}
        with open(CONFIG_FILE, "w") as file:
            json.dump(data, file, indent=4)

    def create_widgets(self):
        # Campo para adicionar nova hotstring
        self.add_frame = tk.Frame(self.master)
        self.add_frame.pack(pady=10)

        tk.Label(self.add_frame, text="Trigger:").grid(row=0, column=0, padx=5)
        self.trigger_entry = tk.Entry(self.add_frame)
        self.trigger_entry.grid(row=0, column=1, padx=5)

        tk.Label(self.add_frame, text="Replacement:").grid(row=0, column=2, padx=5)
        self.replacement_entry = tk.Entry(self.add_frame)
        self.replacement_entry.grid(row=0, column=3, padx=5)

        tk.Label(self.add_frame, text="Category:").grid(row=0, column=4, padx=5)
        self.category_entry = tk.Entry(self.add_frame)
        self.category_entry.grid(row=0, column=5, padx=5)

        tk.Button(self.add_frame, text="Add", command=self.add_hotstring).grid(row=0, column=6, padx=5)

        # Lista de hotstrings
        self.tree = ttk.Treeview(self.master, columns=("trigger", "replacement", "category"), show="headings")
        self.tree.heading("trigger", text="Trigger")
        self.tree.heading("replacement", text="Replacement")
        self.tree.heading("category", text="Category")
        self.tree.pack(pady=10)

        self.load_tree()

        # Campo para busca
        self.search_frame = tk.Frame(self.master)
        self.search_frame.pack(pady=10)

        tk.Label(self.search_frame, text="Search:").grid(row=0, column=0, padx=5)
        self.search_entry = tk.Entry(self.search_frame)
        self.search_entry.grid(row=0, column=1, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_hotstrings)

        tk.Label(self.search_frame, text="Category:").grid(row=0, column=2, padx=5)
        self.category_combobox = ttk.Combobox(self.search_frame, values=self.get_categories())
        self.category_combobox.grid(row=0, column=3, padx=5)
        self.category_combobox.bind("<<ComboboxSelected>>", self.filter_by_category)

    def get_categories(self):
        categories = set(hotstring["category"] for hotstring in self.hotstrings)
        return ["All"] + list(categories)

    def load_tree(self):
        for hotstring in self.hotstrings:
            self.tree.insert("", "end", values=(hotstring["trigger"], hotstring["replacement"], hotstring["category"]))

    def add_hotstring(self):
        trigger = self.trigger_entry.get()
        replacement = self.replacement_entry.get()
        category = self.category_entry.get()

        if not trigger or not replacement or not category:
            messagebox.showwarning("Warning", "All fields must be filled!")
            return

        hotstring = {"trigger": trigger, "replacement": replacement, "category": category}
        self.hotstrings.append(hotstring)
        self.save_hotstrings()

        self.tree.insert("", "end", values=(trigger, replacement, category))
        self.trigger_entry.delete(0, tk.END)
        self.replacement_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)

        # Reconfigurar hotstrings após adicionar
        self.setup_hotstring_listener()

    def search_hotstrings(self, event):
        query = self.search_entry.get().lower()
        for item in self.tree.get_children():
            self.tree.delete(item)

        for hotstring in self.hotstrings:
            if query in hotstring["trigger"].lower() or query in hotstring["replacement"].lower():
                self.tree.insert("", "end", values=(hotstring["trigger"], hotstring["replacement"], hotstring["category"]))

    def filter_by_category(self, event):
        selected_category = self.category_combobox.get()
        for item in self.tree.get_children():
            self.tree.delete(item)

        for hotstring in self.hotstrings:
            if selected_category == "All" or hotstring["category"] == selected_category:
                self.tree.insert("", "end", values=(hotstring["trigger"], hotstring["replacement"], hotstring["category"]))

    def setup_hotstring_listener(self):
        # Remove listeners existentes
        keyboard.unhook_all()

        # Adicionar hotstrings
        for hotstring in self.hotstrings:
            trigger = hotstring["trigger"]
            replacement = hotstring["replacement"]
            print(f"Adding hotstring: '{trigger}' -> '{replacement}'")  # Adicione este print para depuração
            keyboard.add_abbreviation(trigger, replacement)

    def start_keyboard_listener(self):
        # Iniciar o monitoramento dos eventos de teclado
        print("Hotstring listener active. Press 'esc' to exit.")
        keyboard.wait("esc")  # Use a tecla 'esc' para terminar o script

if __name__ == "__main__":
    root = tk.Tk()
    app = HotstringManager(root)
    root.mainloop()
