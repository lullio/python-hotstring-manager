import json
import tkinter as tk
from tkinter import ttk, messagebox
import keyboard
import threading
import re
import time
import ast
import datetime

# import ctypes
# import subprocess
# import os
# import sys
import pyuac


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

        # Primeira linha: Trigger, Replacement e Prefix
        tk.Label(self.add_frame, text="Trigger:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.trigger_entry = tk.Entry(self.add_frame)
        self.trigger_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Label(self.add_frame, text="Replacement:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.replacement_entry = tk.Entry(self.add_frame)
        self.replacement_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        tk.Label(self.add_frame, text="Prefix:").grid(row=0, column=4, padx=5, pady=5, sticky="w")
        self.prefix_entry = tk.Entry(self.add_frame)
        self.prefix_entry.grid(row=0, column=5, padx=5, pady=5, sticky="ew")

        # Segunda linha: Category, BackCount e Botão Add
        tk.Label(self.add_frame, text="Category:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.category_combobox = ttk.Combobox(self.add_frame, values=self.get_categories(), state="normal")
        self.category_combobox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        self.category_combobox.bind("<FocusOut>", self.on_category_combobox_focus_out)

        tk.Label(self.add_frame, text="BackCount:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
        self.backcount_spinbox = tk.Spinbox(self.add_frame, from_=0, to=100, width=5)  # Valor de 0 a 100
        self.backcount_spinbox.grid(row=1, column=3, padx=5, pady=5, sticky="ew")

        tk.Button(self.add_frame, text="Add", command=self.add_hotstring).grid(row=1, column=4, padx=5, pady=5)

        # Lista de hotstrings
        self.tree = ttk.Treeview(self.master, columns=("trigger", "replacement", "category", "prefix", "backCount"), show="headings")
        self.tree.heading("trigger", text="Trigger")
        self.tree.heading("replacement", text="Replacement")
        self.tree.heading("category", text="Category")
        self.tree.heading("prefix", text="Prefix")
        self.tree.heading("backCount", text="backCount")
        self.tree.pack(pady=10, fill="both", expand=True)
        
        # Define a largura das colunas para 0 para escondê-las
        self.tree.column("category", width=0, stretch=tk.NO)
        self.tree.column("prefix", width=0, stretch=tk.NO)
        self.tree.column("backCount", width=0, stretch=tk.NO)



        self.load_tree()

        # Campo para busca
        self.search_frame = tk.Frame(self.master)
        self.search_frame.pack(pady=10)

        tk.Label(self.search_frame, text="Search:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.search_entry = tk.Entry(self.search_frame)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.search_hotstrings)

        tk.Label(self.search_frame, text="Category:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.filter_combobox = ttk.Combobox(self.search_frame, values=self.get_categories())
        self.filter_combobox.grid(row=0, column=3, padx=5, pady=5, sticky="ew")
        self.filter_combobox.bind("<<ComboboxSelected>>", self.filter_by_category)
        # Botão de delete
        tk.Button(self.master, text="Delete", command=self.delete_hotstring).pack(pady=10)
        # tk.Button(self.master, text="Delete", command=self.delete_hotstring).grid(row=1, column=4, padx=5, pady=5)



    def get_categories(self):
        categories = set(hotstring["category"] for hotstring in self.hotstrings)
        return ["All"] + list(categories)

    def load_tree(self):
        for hotstring in self.hotstrings:
            triggers = ', '.join(hotstring["triggers"])
            # self.tree.insert("", "end", values=(triggers, hotstring["replacement"], hotstring["category"], hotstring["prefix"]))
            self.tree.insert("", "end", values=(triggers, hotstring["replacement"], hotstring["category"], hotstring["prefix"], hotstring.get("backCount", 0)))


    def add_hotstring(self):
        triggers = self.trigger_entry.get().split(',') # Aceita múltiplos triggers separados por vírgula
        replacement = self.replacement_entry.get()
        category = self.category_combobox.get()
        prefix = self.prefix_entry.get()
        back_count = self.backcount_spinbox.get() or 0  # Novo campo para backCount, padrão "0"

        if not triggers or not replacement:
            messagebox.showwarning("Warning", "Trigger and Replacement fields must be filled!")
            return
        
        triggers = [trigger.strip() for trigger in triggers]  # Remove espaços extras

        # Se a categoria não estiver na lista, adiciona a nova categoria
        if category not in self.get_categories():
            self.category_combobox["values"] = self.get_categories() + [category]

        # hotstring = {"triggers": triggers, "replacement": replacement, "category": category, "prefix": prefix}
        hotstring = {"triggers": triggers, "replacement": replacement, "category": category, "prefix": prefix, "backCount": int(back_count)}
        self.hotstrings.append(hotstring)
        self.save_hotstrings()

        # self.tree.insert("", "end", values=(trigger, replacement, category, prefix))
        self.tree.insert("", "end", values=(', '.join(triggers), replacement, category, prefix, back_count))
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

        triggers, replacement, category, prefix, back_count = item_values

        # Corrige a busca pela hotstring a ser removida
        # Formata os triggers como uma lista de strings
        triggers_list = triggers.split(', ')
        # self.hotstrings = [hs for hs in self.hotstrings if not (hs["trigger"] == triggers and hs["replacement"] == replacement)]
        
        # Remove o hotstring da lista
        self.hotstrings = [hs for hs in self.hotstrings if not (
            set(hs["triggers"]) == set(triggers_list) and
            hs["replacement"] == replacement and
            hs["category"] == category and
            hs["prefix"] == prefix and
            str(hs.get("backCount", 0)) == back_count  # Comparar backCount como string
        )]
        
        # Atualiza o arquivo de configuração
        self.save_hotstrings()

        # Remove a hotstring da Treeview
        self.tree.delete(selected_item)

        # Reconfigurar hotstrings após exclusão
        self.setup_hotstring_listener()

    def setup_hotstring_listener(self):
        # Remove listeners
        keyboard.unhook_all()

        # Adicionar hotstrings
        for hotstring in self.hotstrings:
            triggers = hotstring["triggers"]
            replacement = hotstring["replacement"]
            prefix = hotstring["prefix"]
            back_count = hotstring.get("backCount", 0)
            # if prefix:
            #     # trigger = prefix + trigger  # Adiciona o prefixo ao trigger
            #     triggers = [prefix + trigger for trigger in triggers]  # Adiciona o prefixo a cada trigger
            for trigger in triggers:
                # print(f"Adding hotstring: '{trigger}' -> '{replacement}'")  # Adicione este print para depuração
                # keyboard.add_abbreviation(trigger, replacement)
                print(f"Adding hotstring: '{trigger}' -> '{replacement}' with backCount: {back_count}")  # Adicione este print para depuração
                # Adicionar o listener para detectar o texto digitado e substituir
                keyboard.add_word_listener(
                    trigger,
                    self.create_callback(trigger, replacement, back_count),
                    triggers=['space'],
                    match_suffix=False,
                    timeout=25
                )
                # keyboard.add_abbreviation(trigger, lambda: replace_with_back_count(replacement, back_count))
                # keyboard.add_abbreviation(trigger, lambda: self.replace_with_back_count(replacement, back_count))
                # keyboard.add_abbreviation(trigger, lambda: self.replace_with_back_count(replacement, back_count))
    def create_callback(self, trigger, replacement, back_count):
        def callback():
            # Remove o texto digitado com backspace
            trigger_length = len(trigger)+1
            for _ in range(trigger_length):
                keyboard.press_and_release('backspace')
                time.sleep(0.01)  # Pequena pausa para garantir que o backspace é registrado
                
            # try:
            #     # Verifica se o código é sintaticamente válido
            #     ast.parse(replacement)
                
            #     # Executa o código se for válido
            #     exec_globals = {}
            #     exec_locals = {}
            #     exec(replacement, exec_globals, exec_locals)
                
            #     # Retorna o resultado, assumindo que a variável 'result' está definida
            #     result = exec_locals.get('result', "Nada")
            #     print(result)
            # except SyntaxError:
            #     # Código inválido
            #     result = replacement
            if replacement.startswith("python "):
                # Remove o prefixo 'python ' do replacement
                code = replacement[len("python "):]
                
                try:
                    # Verifica se o código é sintaticamente válido
                    ast.parse(code)
                    
                    # Executa o código se for válido
                    exec_globals = {}
                    exec_locals = {}
                    exec(code, exec_globals, exec_locals)
                    
                    # Retorna o resultado, assumindo que a variável 'result' está definida
                    result = exec_locals.get('result', 'Nenhum resultado encontrado.')
                    keyboard.write(result)
                    
                except SyntaxError as e:
                    # Retorna a mensagem de erro de sintaxe
                    return f"Erro de sintaxe: {e}"
                except Exception as e:
                    # Retorna qualquer outro erro
                    return f"Erro durante a execução: {e}"
            else:
                keyboard.write(replacement)
                time.sleep(0.01)  # Pequena pausa para garantir que o texto seja escrito
                # Simula pressionar a tecla Left `back_count` vezes
                for _ in range(back_count):
                    keyboard.press_and_release('left')
                    time.sleep(0.01)  # Pequena pausa para garantir que o movimento do cursor é registrado


        return callback
    def execute_backspace(self, replacement, back_count):
        # Digita o texto de substituição
        keyboard.write(replacement)
        time.sleep(0.0)  # Pequena pausa para garantir que o texto seja escrito

        # Simula pressionar a tecla Backspace `back_count` vezes
        for _ in range(back_count):
            # keyboard.press_and_release('backspace')
            keyboard.press_and_release('left')
            time.sleep(0.00)  # Pequena pausa para garantir que o backspace é registrado

    def start_keyboard_listener(self):
        # Iniciar o monitoramento dos eventos de teclado
        print("Hotstring listener active. Press 'esc' to exit.")
        keyboard.wait("shift+ctrl+esc")  # Use a tecla 'esc' para terminar o script
        
if __name__ == "__main__":
    if not pyuac.isUserAdmin():
        print("Re-launching as admin!")
        pyuac.runAsAdmin()
    else:
        root = tk.Tk()
        app = HotstringManager(root)
        root.mainloop()

