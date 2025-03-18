#**
#
#  Copyright 2022-2025 Cyril John Magayaga (https://www.github.com/magayaga)
#  CyCode Studio (v2.0)
# 
# *#
from tkinter import Menu, BooleanVar

def toggle_word_wrap(text, word_wrap_var):
    """Toggle word wrap on and off."""
    if word_wrap_var.get():
        text.config(wrap="word")  # Enable word wrap
    else:
        text.config(wrap="none")  # Disable word wrap

def main(root, text, menubar):
    view_menu = Menu(menubar, tearoff=0)

    # Word Wrap Option
    word_wrap_var = BooleanVar(value=True)  # Default: Enabled
    root.word_wrap_var = word_wrap_var  # Store in root to persist state
    view_menu.add_checkbutton(label="Word Wrap", variable=word_wrap_var, command=lambda: toggle_word_wrap(text, word_wrap_var))

    # Add View Menu to the Menubar
    menubar.add_cascade(label="View", menu=view_menu)
