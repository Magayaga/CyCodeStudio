#**
#
#  Copyright 2022-2025 Cyril John Magayaga (https://www.github.com/magayaga)
#  CyCode Studio (v2.0)
#
# *#
from tkinter import *
from tkinter.filedialog import *
from tkinter.messagebox import *
from tkinter.font import *
from tkinter.scrolledtext import *
from tkinter import ttk
import tkinter as tk
import file_menu, edit_menu, format_menu, view_menu, help_menu
from syntax_highlighting import apply_syntax_highlighting

# History
class History(list):
    def __getitem__(self, index):
        try:
            return list.__getitem__(self, index)
        except IndexError:
            return

if __name__ == '__main__':
    # First Window
    root = Tk()
    root.title("CyCode Studio")
    root.geometry("800x600")
    root.minsize(width=750, height=500)

    # Paned Window
    panedWindow = ttk.PanedWindow(orient=tk.HORIZONTAL)

    # First Text Editor
    tabControl = ttk.Notebook(root)
    textEditor = ttk.Frame(tabControl)
    tabControl.add(textEditor)
    tabControl.pack(expand=True, fill="both")

    # First ListBox
    left_list = tk.Listbox(tabControl)
    left_list.pack(side=tk.BOTTOM)
    panedWindow.add(tabControl)

    # First Text
    word_wrap_default = True  # Set word wrap ON by default
    text = ScrolledText(root, state="normal", height=28, width=400, wrap="word" if word_wrap_default else "none", pady=2, padx=3, undo=True)
    text.pack(expand=True, fill="both", side=TOP)
    text.focus_set()

    # Apply Syntax Highlighting
    apply_syntax_highlighting(text, "python")  # Default syntax is Python

    # Menubar
    menubar = Menu(root)
    file_menu.main(root, text, menubar)
    edit_menu.main(root, text, menubar)
    format_menu.main(root, text, menubar)
    view_menu.main(root, text, menubar)
    help_menu.main(root, text, menubar)

    # Run the Window
    root.mainloop()
