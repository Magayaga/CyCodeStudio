#**
#
#  Copyright 2022-2023 Cyril John Magayaga (https://www.github.com/magayaga)
#  CyCode Studio (v2.0)
# 
# *#
from tkinter import *
from tkinter.messagebox import *
from tkinter.ttk import *
import webbrowser

class Help():
    def about(root):
        newAbout = Toplevel()
        newAbout.title("About")
        newAbout.geometry("350x150")
        Label(newAbout, justify="center", wraplength="300", text="CyCode Studio is a source-code editor developed by Cyril John Magayaga\n\nCopyright 2022-2023 Cyril John Magayaga", font=("Arial 11")).pack(pady=30)
    
    def license(root):
        webbrowser.open("https://github.com/Magayaga/CyCodeStudio/blob/main/LICENSE")


def main(root, text, menubar):

    help = Help()

    helpMenu = Menu(menubar)
    helpMenu.add_command(label="View License", command=help.license)
    helpMenu.add_separator()
    helpMenu.add_command(label="About", command=help.about)
    menubar.add_cascade(label="Help", menu=helpMenu)

    root.config(menu=menubar)


if __name__ == "__main__":
    print("Please run 'help_menu.py'")