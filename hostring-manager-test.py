import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import json
import re

class HotstringManager:
    def __init__(self):
        self.hotstrings = {}
        self.load_hotstrings()

        self.root = tk.Tk()
        self.root.title("Hotstring Manager")

        # GUI elements
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(padx=10, pady=10)

        self.search_frame = tk.Frame(self.main_frame)
        self.search_frame.pack()

        self.search_label = tk.Label(self.search_frame, text="Search:")
        self.search_label.pack(side=tk.LEFT)

        self.search_entry = tk.Entry(self.search_frame)
        self.search_entry.pack(side=tk.LEFT)
        self.search_entry.bind("<KeyRelease>", self.update_list_view)

        self.list_frame = tk.Frame(self.main_frame)
        self.list_frame.pack()

        self.list_view = ttk.Treeview(self.list_frame, columns=("options", "abbreviation", "replacement", "comment"), show="headings")
        self.list_view.heading("options", text="Options")
        self.list_view.heading("abbreviation", text="Abbreviation")
        self.list_view.heading("replacement", text="Replacement")
        self.list_view.heading("comment", text="Comment")
        self.list_view.pack(side=tk.LEFT)

        self.list_view.bind("<<TreeviewSelect>>", self.select_hotstring)
        self.list_view.bind("<Double-1>", self.trigger_hotstring)

        self.scrollbar = ttk.Scrollbar(self.list_frame, orient="vertical", command=self.list_view.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill="y")
        self.list_view.configure(yscrollcommand=self.scrollbar.set)

        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack()

        self.add_button = tk.Button(self.button_frame, text="Add", command=self.add_hotstring)
        self.add_button.pack(side=tk.LEFT)

        self.edit_button = tk.Button(self.button_frame, text="Edit", command=self.edit_hotstring)
        self.edit_button.pack(side=tk.LEFT)

        self.delete_button = tk.Button(self.button_frame, text="Delete", command=self.delete_hotstring)
        self.delete_button.pack(side=tk.LEFT)

        self.update_list_view()

        self.root.mainloop()

    # Helper Functions
    def load_hotstrings(self):
        try:
            with open("hotstrings.json", "r") as f:
                self.hotstrings = json.load(f)
        except FileNotFoundError:
            pass

    def save_hotstrings(self):
        with open("hotstrings.json", "w") as f:
            json.dump(self.hotstrings, f)

    def escape_cc(self, text):
        text = text.replace("\n", "``n")
        text = text.replace("\t", "``t")
        text = text.replace("\b", "``b")
        return text

    def unescape_cc(self, text):
        text = text.replace("``n", "\n")
        text = text.replace("``t", "\t")
        text = text.replace("``b", "\b")
        return text

    # GUI Event Handlers
    def update_list_view(self, event=None):
        self.list_view.delete(*self.list_view.get_children())
        search_term = self.search_entry.get().lower()

        for key, value in self.hotstrings.items():
            options, abbreviation = key.split(":")
            replacement, comment = value.split(" `;", 1) if " `;" in value else (value, "")
            
            if search_term in abbreviation.lower() or search_term in replacement.lower() or search_term in comment.lower():
                self.list_view.insert("", tk.END, values=(options, abbreviation, replacement, comment))

    def select_hotstring(self, event):
        selected_item = self.list_view.selection()[0]
        options, abbreviation, replacement, comment = self.list_view.item(selected_item, "values")
        self.selected_hotstring = {
            "options": options,
            "abbreviation": abbreviation,
            "replacement": replacement,
            "comment": comment,
        }

    def add_hotstring(self):
        def save_hotstring():
            options = ""
            if no_end_char_var.get():
                options += "*"
            if case_sensitive_var.get():
                options += "C"
            if trigger_inside_var.get():
                options += "?"
            if no_conform_case_var.get():
                options += "C1"
            if no_auto_back_var.get():
                options += "B0"
            if omit_end_char_var.get():
                options += "O"
            if send_raw_var.get():
                options += "R"
            if text_raw_var.get():
                options += "T"
            if execute_var.get():
                options += "X"

            abbreviation = abbreviation_entry.get()
            replacement = replacement_entry.get()
            comment = comment_entry.get()

            if not abbreviation or not replacement:
                messagebox.showwarning("Error", "Please enter an abbreviation and replacement text.")
                return

            self.hotstrings[f"{options}:{abbreviation}"] = f"{replacement} `;" + comment
            self.save_hotstrings()
            self.update_list_view()
            add_window.destroy()

        add_window = tk.Toplevel(self.root)
        add_window.title("Add Hotstring")

        abbreviation_label = tk.Label(add_window, text="Abbreviation:")
        abbreviation_label.grid(row=0, column=0, padx=5, pady=5)

        abbreviation_entry = tk.Entry(add_window)
        abbreviation_entry.grid(row=0, column=1, padx=5, pady=5)

        replacement_label = tk.Label(add_window, text="Replacement:")
        replacement_label.grid(row=1, column=0, padx=5, pady=5)

        replacement_entry = tk.Entry(add_window)
        replacement_entry.grid(row=1, column=1, padx=5, pady=5)

        comment_label = tk.Label(add_window, text="Comment:")
        comment_label.grid(row=2, column=0, padx=5, pady=5)

        comment_entry = tk.Entry(add_window)
        comment_entry.grid(row=2, column=1, padx=5, pady=5)

        # Options
        no_end_char_var = tk.BooleanVar()
        case_sensitive_var = tk.BooleanVar()
        trigger_inside_var = tk.BooleanVar()
        no_conform_case_var = tk.BooleanVar()
        no_auto_back_var = tk.BooleanVar()
        omit_end_char_var = tk.BooleanVar()
        send_raw_var = tk.BooleanVar()
        text_raw_var = tk.BooleanVar()
        execute_var = tk.BooleanVar()

        no_end_char_checkbox = tk.Checkbutton(add_window, text="No Ending Character (*)", variable=no_end_char_var)
        no_end_char_checkbox.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        case_sensitive_checkbox = tk.Checkbutton(add_window, text="Case Sensitive (C)", variable=case_sensitive_var)
        case_sensitive_checkbox.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        trigger_inside_checkbox = tk.Checkbutton(add_window, text="Trigger Inside Another Word (?)", variable=trigger_inside_var)
        trigger_inside_checkbox.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        no_conform_case_checkbox = tk.Checkbutton(add_window, text="Do Not Conform To Typed Case (C1)", variable=no_conform_case_var)
        no_conform_case_checkbox.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

        no_auto_back_checkbox = tk.Checkbutton(add_window, text="No Automatic Backspacing (B0)", variable=no_auto_back_var)
        no_auto_back_checkbox.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

        omit_end_char_checkbox = tk.Checkbutton(add_window, text="Omit Ending Character (O)", variable=omit_end_char_var)
        omit_end_char_checkbox.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

        send_raw_checkbox = tk.Checkbutton(add_window, text="Send Raw (R)", variable=send_raw_var)
        send_raw_checkbox.grid(row=9, column=0, columnspan=2, padx=5, pady=5)

        text_raw_checkbox = tk.Checkbutton(add_window, text="Send Text Raw (T)", variable=text_raw_var)
        text_raw_checkbox.grid(row=10, column=0, columnspan=2, padx=5, pady=5)

        execute_checkbox = tk.Checkbutton(add_window, text="Run/Execute (X)", variable=execute_var)
        execute_checkbox.grid(row=11, column=0, columnspan=2, padx=5, pady=5)

        save_button = tk.Button(add_window, text="Save", command=save_hotstring)
        save_button.grid(row=12, column=0, columnspan=2, padx=5, pady=5)

    def edit_hotstring(self):
        if not hasattr(self, "selected_hotstring"):
            messagebox.showwarning("Error", "Please select a hotstring to edit.")
            return

        def save_edit():
            options = ""
            if no_end_char_var.get():
                options += "*"
            if case_sensitive_var.get():
                options += "C"
            if trigger_inside_var.get():
                options += "?"
            if no_conform_case_var.get():
                options += "C1"
            if no_auto_back_var.get():
                options += "B0"
            if omit_end_char_var.get():
                options += "O"
            if send_raw_var.get():
                options += "R"
            if text_raw_var.get():
                options += "T"
            if execute_var.get():
                options += "X"

            abbreviation = abbreviation_entry.get()
            replacement = replacement_entry.get()
            comment = comment_entry.get()

            if not abbreviation or not replacement:
                messagebox.showwarning("Error", "Please enter an abbreviation and replacement text.")
                return

            del self.hotstrings[f"{self.selected_hotstring['options']}:{self.selected_hotstring['abbreviation']}"]
            self.hotstrings[f"{options}:{abbreviation}"] = f"{replacement} `;" + comment
            self.save_hotstrings()
            self.update_list_view()
            edit_window.destroy()

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Hotstring")

        abbreviation_label = tk.Label(edit_window, text="Abbreviation:")
        abbreviation_label.grid(row=0, column=0, padx=5, pady=5)

        abbreviation_entry = tk.Entry(edit_window)
        abbreviation_entry.grid(row=0, column=1, padx=5, pady=5)
        abbreviation_entry.insert(0, self.selected_hotstring["abbreviation"])

        replacement_label = tk.Label(edit_window, text="Replacement:")
        replacement_label.grid(row=1, column=0, padx=5, pady=5)

        replacement_entry = tk.Entry(edit_window)
        replacement_entry.grid(row=1, column=1, padx=5, pady=5)
        replacement_entry.insert(0, self.selected_hotstring["replacement"])

        comment_label = tk.Label(edit_window, text="Comment:")
        comment_label.grid(row=2, column=0, padx=5, pady=5)

        comment_entry = tk.Entry(edit_window)
        comment_entry.grid(row=2, column=1, padx=5, pady=5)
        comment_entry.insert(0, self.selected_hotstring["comment"])

        # Options
        no_end_char_var = tk.BooleanVar(value=("*" in self.selected_hotstring["options"]))
        case_sensitive_var = tk.BooleanVar(value=("C" in self.selected_hotstring["options"]))
        trigger_inside_var = tk.BooleanVar(value=("?" in self.selected_hotstring["options"]))
        no_conform_case_var = tk.BooleanVar(value=("C1" in self.selected_hotstring["options"]))
        no_auto_back_var = tk.BooleanVar(value=("B0" in self.selected_hotstring["options"]))
        omit_end_char_var = tk.BooleanVar(value=("O" in self.selected_hotstring["options"]))
        send_raw_var = tk.BooleanVar(value=("R" in self.selected_hotstring["options"]))
        text_raw_var = tk.BooleanVar(value=("T" in self.selected_hotstring["options"]))
        execute_var = tk.BooleanVar(value=("X" in self.selected_hotstring["options"]))

        no_end_char_checkbox = tk.Checkbutton(edit_window, text="No Ending Character (*)", variable=no_end_char_var)
        no_end_char_checkbox.grid(row=3, column=0, columnspan=2, padx=5, pady=5)

        case_sensitive_checkbox = tk.Checkbutton(edit_window, text="Case Sensitive (C)", variable=case_sensitive_var)
        case_sensitive_checkbox.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

        trigger_inside_checkbox = tk.Checkbutton(edit_window, text="Trigger Inside Another Word (?)", variable=trigger_inside_var)
        trigger_inside_checkbox.grid(row=5, column=0, columnspan=2, padx=5, pady=5)

        no_conform_case_checkbox = tk.Checkbutton(edit_window, text="Do Not Conform To Typed Case (C1)", variable=no_conform_case_var)
        no_conform_case_checkbox.grid(row=6, column=0, columnspan=2, padx=5, pady=5)

        no_auto_back_checkbox = tk.Checkbutton(edit_window, text="No Automatic Backspacing (B0)", variable=no_auto_back_var)
        no_auto_back_checkbox.grid(row=7, column=0, columnspan=2, padx=5, pady=5)

        omit_end_char_checkbox = tk.Checkbutton(edit_window, text="Omit Ending Character (O)", variable=omit_end_char_var)
        omit_end_char_checkbox.grid(row=8, column=0, columnspan=2, padx=5, pady=5)

        send_raw_checkbox = tk.Checkbutton(edit_window, text="Send Raw (R)", variable=send_raw_var)
        send_raw_checkbox.grid(row=9, column=0, columnspan=2, padx=5, pady=5)

        text_raw_checkbox = tk.Checkbutton(edit_window, text="Send Text Raw (T)", variable=text_raw_var)
        text_raw_checkbox.grid(row=10, column=0, columnspan=2, padx=5, pady=5)

        execute_checkbox = tk.Checkbutton(edit_window, text="Run/Execute (X)", variable=execute_var)
        execute_checkbox.grid(row=11, column=0, columnspan=2, padx=5, pady=5)

        save_button = tk.Button(edit_window, text="Save", command=save_edit)
        save_button.grid(row=12, column=0, columnspan=2, padx=5, pady=5)

    def delete_hotstring(self):
        if not hasattr(self, "selected_hotstring"):
            messagebox.showwarning("Error", "Please select a hotstring to delete.")
            return

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the hotstring '{self.selected_hotstring['abbreviation']}'?"):
            del self.hotstrings[f"{self.selected_hotstring['options']}:{self.selected_hotstring['abbreviation']}"]
            self.save_hotstrings()
            self.update_list_view()

    def trigger_hotstring(self, event):
        selected_item = self.list_view.selection()[0]
        options, abbreviation, replacement, comment = self.list_view.item(selected_item, "values")

        replacement = self.unescape_cc(replacement)
        print(f"Sending: {replacement}")

if __name__ == "__main__":
    HotstringManager()


# **Explanation:**

# 1. **Import necessary libraries:**
#    - `tkinter` for GUI elements.
#    - `json` for loading and saving hotstrings data.
#    - `re` for regular expressions.

# 2. **Define the `HotstringManager` class:**
#    - **`__init__` method:**
#      - Initializes an empty dictionary `self.hotstrings` to store hotstrings.
#      - Loads existing hotstrings from `hotstrings.json` if it exists.
#      - Creates the main window (`self.root`) and sets the title.
#      - Creates various GUI elements (frames, labels, entries, listview, buttons) and positions them.
#      - Binds event handlers for search entry, listview selection, and double-click.
#      - Calls `update_list_view` to initially populate the listview.
#      - Starts the main event loop (`self.root.mainloop()`).
#    - **Helper Functions:**
#      - `load_hotstrings`: Loads hotstrings from `hotstrings.json`.
#      - `save_hotstrings`: Saves hotstrings to `hotstrings.json`.
#      - `escape_cc`: Escapes control characters in replacement text for storage.
#      - `unescape_cc`: Unescapes control characters in replacement text for sending.
#    - **GUI Event Handlers:**
#      - `update_list_view`: Updates the listview based on search term.
#      - `select_hotstring`: Saves the selected hotstring details to `self.selected_hotstring`.
#      - `add_hotstring`: Opens a dialog to add a new hotstring.
#      - `edit_hotstring`: Opens a dialog to edit the selected hotstring.
#      - `delete_hotstring`: Deletes the selected hotstring.
#      - `trigger_hotstring`: Sends the replacement text of the selected hotstring.

# 3. **GUI elements:**
#    - **Frames:** `main_frame`, `search_frame`, `list_frame`, `button_frame`.
#    - **Labels:** `search_label`, `abbreviation_label`, `replacement_label`, `comment_label`.
#    - **Entry widgets:** `search_entry`, `abbreviation_entry`, `replacement_entry`, `comment_entry`.
#    - **Listview:** `list_view` with columns for options, abbreviation, replacement, and comment.
#    - **Buttons:** `add_button`, `edit_button`, `delete_button`, `save_button`.
#    - **Checkbuttons:** To enable/disable various hotstring options.

# 4. **Main execution (`if __name__ == "__main__":`)**:
#    - Creates an instance of `HotstringManager()`, which starts the application.

# **To use this program:**

# 1. Save the code as a Python file (e.g., `hotstring_manager.py`).
# 2. Run the file from your terminal: `python hotstring_manager.py`.
# 3. The Hotstring Manager GUI will appear.
# 4. You can add, edit, delete, and search for hotstrings using the provided interface.
# 5. The hotstrings data will be saved in `hotstrings.json` when you close the application.

# **Note:** This program provides a GUI to manage hotstrings, but it doesn't actually implement the hotstring functionality like AutoHotkey does. You'll need to find a separate solution for hotstring injection if you want to use these hotstrings in other applications.
