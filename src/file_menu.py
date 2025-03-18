#**
#
#  Copyright 2022-2025 Cyril John Magayaga (https://www.github.com/magayaga)
#  CyCode Studio (v2.0)
# 
# *#
from tkinter import *
from tkinter.filedialog import *
from tkinter.messagebox import *
from tkinter.scrolledtext import *
from tkinter.font import *
import os
import subprocess
import sys

class File():
    def newFile(self):
        self.filename = "Untitled"
        self.text.delete(0.0, END)

    def openFile(self):
        f = askopenfile(mode='r')
        if f is not None:
            self.filename = f.name
            t = f.read()
            self.text.delete(0.0, END)
            self.text.insert(0.0, t)

    def saveFile(self):
        try:
            t = self.text.get(0.0, END)
            with open(self.filename, 'w') as f:
                f.write(t)
        except:
            self.saveAs()

    def saveAs(self):
        f = asksaveasfile(mode='w', defaultextension='.txt')
        if f:
            t = self.text.get(0.0, END)
            try:
                f.write(t.rstrip())
            except:
                showerror(title="Oops!", message="Unable to save file...")

    def quit(self):
        entry = askyesno(title="Exit", message="Are you sure you want to quit?")
        if entry:
            self.root.destroy()

    def __init__(self, text, root):
        self.filename = None
        self.text = text
        self.root = root

def main(root, text, menubar):
    filemenu = Menu(menubar, tearoff=0)
    objFile = File(text, root)

    filemenu.add_command(label="New File", command=objFile.newFile)
    filemenu.add_command(label="Open File", command=objFile.openFile)
    filemenu.add_separator()
    filemenu.add_command(label="Save File", command=objFile.saveFile)
    filemenu.add_command(label="Save As...", command=objFile.saveAs)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=objFile.quit)

    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu=menubar)

if __name__ == "__main__":
    print("Please run 'file_menu.py'")
