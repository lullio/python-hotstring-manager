import json
import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import threading
import re

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
        self.category_combobox = ttk.Combobox(self.add_frame, values=self.get_categories(), state="normal")
        self.category_combobox.grid(row=0, column=5, padx=5)
        self.category_combobox.bind("<FocusOut>", self.on_category_combobox_focus_out)  # Verifica se uma nova categoria foi inserida

        tk.Label(self.add_frame, text="Prefix:").grid(row=0, column=6, padx=5)
        self.prefix_entry = tk.Entry(self.add_frame)
        self.prefix_entry.grid(row=0, column=7, padx=5)

        tk.Button(self.add_frame, text="Add", command=self.add_hotstring).grid(row=0, column=8, padx=5)

        # Lista de hotstrings
        self.tree = ttk.Treeview(self.master, columns=("trigger", "replacement", "category", "prefix"), show="headings")
        self.tree.heading("trigger", text="Trigger")
        self.tree.heading("replacement", text="Replacement")
        self.tree.heading("category", text="Category")
        self.tree.heading("prefix", text="Prefix")
        self.tree.pack(pady=10)

        # Botão de delete
        tk.Button(self.master, text="Delete", command=self.delete_hotstring).pack(pady=10)

        self.load_tree()

        # Campo para busca
        self.search_frame = tk.Frame(self.master)
        self.search_frame.pack(pady=10)

        tk.Label(self.search_frame, text="Search:").grid(row=0, column=0, padx=5)
        self.search_entry = tk.Entry(self.search_frame)
        self.search_entry.grid(row=0, column=1, padx=5)
        self.search_entry.bind("<KeyRelease>", self.search_hotstrings)

        tk.Label(self.search_frame, text="Category:").grid(row=0, column=2, padx=5)
        self.filter_combobox = ttk.Combobox(self.search_frame, values=self.get_categories())
        self.filter_combobox.grid(row=0, column=3, padx=5)
        self.filter_combobox.bind("<<ComboboxSelected>>", self.filter_by_category)

    def get_categories(self):
        categories = set(hotstring["category"] for hotstring in self.hotstrings)
        return ["All"] + list(categories)

    def load_tree(self):
        for hotstring in self.hotstrings:
            triggers = ', '.join(hotstring["triggers"])
            self.tree.insert("", "end", values=(triggers, hotstring["replacement"], hotstring["category"], hotstring["prefix"]))

    def add_hotstring(self):
        triggers = self.trigger_entry.get().split(',') # Aceita múltiplos triggers separados por vírgula
        replacement = self.replacement_entry.get()
        category = self.category_combobox.get()
        prefix = self.prefix_entry.get()

        if not triggers or not replacement:
            messagebox.showwarning("Warning", "Trigger and Replacement fields must be filled!")
            return
        
        triggers = [trigger.strip() for trigger in triggers]  # Remove espaços extras

        # Se a categoria não estiver na lista, adiciona a nova categoria
        if category not in self.get_categories():
            self.category_combobox["values"] = self.get_categories() + [category]

        hotstring = {"triggers": triggers, "replacement": replacement, "category": category, "prefix": prefix}
        self.hotstrings.append(hotstring)
        self.save_hotstrings()

        # self.tree.insert("", "end", values=(trigger, replacement, category, prefix))
        self.tree.insert("", "end", values=(', '.join(triggers), replacement, category, prefix))
        self.trigger_entry.delete(0, tk.END)
        self.replacement_entry.delete(0, tk.END)
        self.category_combobox.set('')  # Limpa o combobox
        self.prefix_entry.delete(0, tk.END)  # Limpa o campo de prefixo

        # Reconfigurar hotstrings após adicionar
        self.setup_hotstring_listener()

    def on_category_combobox_focus_out(self, event):
        category = self.category_combobox.get()
        if category and category not in self.get_categories():
            self.category_combobox["values"] = self.get_categories() + [category]

    def search_hotstrings(self, event):
        query = self.search_entry.get().strip()  # Remove espaços extras antes e depois da consulta
        if not query:
            # Se a consulta estiver vazia, exibe todos os hotstrings
            self.load_tree()
            return

        # Compila a expressão regular com a consulta, garantindo a correspondência correta
        try:
            pattern = re.compile(query, re.IGNORECASE)  # Usa re.IGNORECASE para corresponder sem distinguir maiúsculas e minúsculas
        except re.error:
            messagebox.showerror("Invalid Regex", "The search query is not a valid regular expression.")
            return

        # Limpa a Treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Insere os hotstrings que correspondem à expressão regular
        for hotstring in self.hotstrings:
            triggers = ', '.join(hotstring["triggers"])  # Concatena todos os triggers em uma string
            replacement = hotstring["replacement"]
            
            # Verifica se a regex corresponde a triggers ou replacement
            if pattern.search(triggers) or pattern.search(replacement):
                self.tree.insert("", "end", values=(
                    ', '.join(hotstring["triggers"]), 
                    hotstring["replacement"], 
                    hotstring["category"], 
                    hotstring["prefix"]
                ))
                
    def filter_by_category(self, event):
        selected_category = self.filter_combobox.get()
        for item in self.tree.get_children():
            self.tree.delete(item)

        for hotstring in self.hotstrings:
            if selected_category == "All" or hotstring["category"] == selected_category:
                triggers = ', '.join(hotstring["triggers"])
                self.tree.insert("", "end", values=(triggers, hotstring["replacement"], hotstring["category"], hotstring["prefix"]))

    def delete_hotstring(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "No hotstring selected for deletion.")
            return

        item_values = self.tree.item(selected_item, "values")
        if not item_values:
            messagebox.showwarning("Warning", "No data found for selected hotstring.")
            return

        triggers, replacement, category, prefix = item_values

        # Corrige a busca pela hotstring a ser removida
        # Formata os triggers como uma lista de strings
        triggers_list = triggers.split(', ')
        # self.hotstrings = [hs for hs in self.hotstrings if not (hs["trigger"] == triggers and hs["replacement"] == replacement)]
        
        # Remove o hotstring da lista
        self.hotstrings = [hs for hs in self.hotstrings if not (
            set(hs["triggers"]) == set(triggers_list) and
            hs["replacement"] == replacement and
            hs["category"] == category and
            hs["prefix"] == prefix
        )]
        
        # Atualiza o arquivo de configuração
        self.save_hotstrings()

        # Remove a hotstring da Treeview
        self.tree.delete(selected_item)

        # Reconfigurar hotstrings após exclusão
        self.setup_hotstring_listener()

    def setup_hotstring_listener(self):
        # Remove listeners existentes
        keyboard.unhook_all()

        # Adicionar hotstrings
        for hotstring in self.hotstrings:
            triggers = hotstring["triggers"]
            replacement = hotstring["replacement"]
            prefix = hotstring["prefix"]
            if prefix:
                # trigger = prefix + trigger  # Adiciona o prefixo ao trigger
                triggers = [prefix + trigger for trigger in triggers]  # Adiciona o prefixo a cada trigger
            for trigger in triggers:
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
