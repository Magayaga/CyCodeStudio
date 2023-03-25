#**
#
#  Copyright 2022-2023 Cyril John Magayaga (https://www.github.com/magayaga)
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
from code import InteractiveConsole
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import idlelib.colorizer as ic, idlelib.percolator as ip
import file_menu, edit_menu, format_menu, help_menu, re, sys
import subprocess


# History
class History(list):
    def __getitem__(self, index):
        try:
            return list.__getitem__(self, index)
        except IndexError:
            return

# Python Shell like TextConsole
class TextConsole(tk.Text):
    def __init__(self, master, **kw):
        kw.setdefault('width', 50)
        kw.setdefault('wrap', 'word')
        kw.setdefault('prompt1', '>>> ')
        kw.setdefault('prompt2', '... ')
        banner = kw.pop('banner', 'Python %s\n' % sys.version)
        self._prompt1 = kw.pop('prompt1')
        self._prompt2 = kw.pop('prompt2')
        tk.Text.__init__(self, master, **kw)
        # History
        self.history = History()
        self._hist_item = 0
        self._hist_match = ''

        # Initialization
        self._console = InteractiveConsole() # python console to execute commands
        self.insert('end', banner, 'banner')
        self.prompt()
        self.mark_set('input', 'insert')
        self.mark_gravity('input', 'left')

        # Bindings
        self.bind('<Control-Return>', self.on_ctrl_return)
        self.bind('<Shift-Return>', self.on_shift_return)
        self.bind('<KeyPress>', self.on_key_press)
        self.bind('<KeyRelease>', self.on_key_release)
        self.bind('<Tab>', self.on_tab)
        self.bind('<Down>', self.on_down)
        self.bind('<Up>', self.on_up)
        self.bind('<Return>', self.on_return)
        self.bind('<BackSpace>', self.on_backspace)
        self.bind('<Control-c>', self.on_ctrl_c)
        self.bind('<<Paste>>', self.on_paste)

    def on_ctrl_c(self, event):
        """Copy selected code, removing prompts first"""
        sel = self.tag_ranges('sel')
        if sel:
            txt = self.get('sel.first', 'sel.last').splitlines()
            lines = []
            for i, line in enumerate(txt):
                if line.startswith(self._prompt1):
                    lines.append(line[len(self._prompt1):])
                elif line.startswith(self._prompt2):
                    lines.append(line[len(self._prompt2):])
                else:
                    lines.append(line)
            self.clipboard_clear()
            self.clipboard_append('\n'.join(lines))
        return 'break'

    def on_paste(self, event):
        """Paste commands"""
        if self.compare('insert', '<', 'input'):
            return "break"
        sel = self.tag_ranges('sel')
        if sel:
            self.delete('sel.first', 'sel.last')
        txt = self.clipboard_get()
        self.insert("insert", txt)
        self.insert_cmd(self.get("input", "end"))
        return 'break'

    def prompt(self, result=False):
        """Insert a prompt"""
        if result:
            self.insert('end', self._prompt2, 'prompt')
        else:
            self.insert('end', self._prompt1, 'prompt')
        self.mark_set('input', 'end-1c')

    def on_key_press(self, event):
        """Prevent text insertion in command history"""
        if self.compare('insert', '<', 'input') and event.keysym not in ['Left', 'Right']:
            self._hist_item = len(self.history)
            self.mark_set('insert', 'input lineend')
            if not event.char.isalnum():
                return 'break'

    def on_key_release(self, event):
        """Reset history scrolling"""
        if self.compare('insert', '<', 'input') and event.keysym not in ['Left', 'Right']:
            self._hist_item = len(self.history)
            return 'break'

    def on_up(self, event):
        """Handle up arrow key press"""
        if self.compare('insert', '<', 'input'):
            self.mark_set('insert', 'end')
            return 'break'
        elif self.index('input linestart') == self.index('insert linestart'):
            # navigate history
            line = self.get('input', 'insert')
            self._hist_match = line
            hist_item = self._hist_item
            self._hist_item -= 1
            item = self.history[self._hist_item]
            while self._hist_item >= 0 and not item.startswith(line):
                self._hist_item -= 1
                item = self.history[self._hist_item]
            if self._hist_item >= 0:
                index = self.index('insert')
                self.insert_cmd(item)
                self.mark_set('insert', index)
            else:
                self._hist_item = hist_item
            return 'break'

    def on_down(self, event):
        """Handle down arrow key press"""
        if self.compare('insert', '<', 'input'):
            self.mark_set('insert', 'end')
            return 'break'
        elif self.compare('insert lineend', '==', 'end-1c'):
            # navigate history
            line = self._hist_match
            self._hist_item += 1
            item = self.history[self._hist_item]
            while item is not None and not item.startswith(line):
                self._hist_item += 1
                item = self.history[self._hist_item]
            if item is not None:
                self.insert_cmd(item)
                self.mark_set('insert', 'input+%ic' % len(self._hist_match))
            else:
                self._hist_item = len(self.history)
                self.delete('input', 'end')
                self.insert('insert', line)
            return 'break'

    def on_tab(self, event):
        """Handle tab key press"""
        if self.compare('insert', '<', 'input'):
            self.mark_set('insert', 'input lineend')
            return "break"
        # indent code
        sel = self.tag_ranges('sel')
        if sel:
            start = str(self.index('sel.first'))
            end = str(self.index('sel.last'))
            start_line = int(start.split('.')[0])
            end_line = int(end.split('.')[0]) + 1
            for line in range(start_line, end_line):
                self.insert('%i.0' % line, '    ')
        else:
            txt = self.get('insert-1c')
            if not txt.isalnum() and txt != '.':
                self.insert('insert', '    ')
        return "break"

    def on_shift_return(self, event):
        """Handle Shift+Return key press"""
        if self.compare('insert', '<', 'input'):
            self.mark_set('insert', 'input lineend')
            return 'break'
        else: # execute commands
            self.mark_set('insert', 'end')
            self.insert('insert', '\n')
            self.insert('insert', self._prompt2, 'prompt')
            self.eval_current(True)

    def on_return(self, event=None):
        """Handle Return key press"""
        if self.compare('insert', '<', 'input'):
            self.mark_set('insert', 'input lineend')
            return 'break'
        else:
            self.eval_current(True)
            self.see('end')
        return 'break'

    def on_ctrl_return(self, event=None):
        """Handle Ctrl+Return key press"""
        self.insert('insert', '\n' + self._prompt2, 'prompt')
        return 'break'

    def on_backspace(self, event):
        """Handle delete key press"""
        if self.compare('insert', '<=', 'input'):
            self.mark_set('insert', 'input lineend')
            return 'break'
        sel = self.tag_ranges('sel')
        if sel:
            self.delete('sel.first', 'sel.last')
        else:
            linestart = self.get('insert linestart', 'insert')
            if re.search(r'    $', linestart):
                self.delete('insert-4c', 'insert')
            else:
                self.delete('insert-1c')
        return 'break'

    def insert_cmd(self, cmd):
        """Insert lines of code, adding prompts"""
        input_index = self.index('input')
        self.delete('input', 'end')
        lines = cmd.splitlines()
        if lines:
            indent = len(re.search(r'^( )*', lines[0]).group())
            self.insert('insert', lines[0][indent:])
            for line in lines[1:]:
                line = line[indent:]
                self.insert('insert', '\n')
                self.prompt(True)
                self.insert('insert', line)
                self.mark_set('input', input_index)
        self.see('end')

    def eval_current(self, auto_indent=False):
        """Evaluate code"""
        index = self.index('input')
        lines = self.get('input', 'insert lineend').splitlines() # commands to execute
        self.mark_set('insert', 'insert lineend')
        if lines:  # there is code to execute
            # remove prompts
            lines = [lines[0].rstrip()] + [line[len(self._prompt2):].rstrip() for line in lines[1:]]
            for i, l in enumerate(lines):
                if l.endswith('?'):
                    lines[i] = 'help(%s)' % l[:-1]
            cmds = '\n'.join(lines)
            self.insert('insert', '\n')
            out = StringIO()  # command output
            err = StringIO()  # command error traceback
            with redirect_stderr(err):     # redirect error traceback to err
                with redirect_stdout(out): # redirect command output
                    # execute commands in interactive console
                    res = self._console.push(cmds)
                    # if res is True, this is a partial command, e.g. 'def test():' and we need to wait for the rest of the code
            errors = err.getvalue()
            if errors:  # there were errors during the execution
                self.insert('end', errors)  # display the traceback
                self.mark_set('input', 'end')
                self.see('end')
                self.prompt() # insert new prompt
            else:
                output = out.getvalue()  # get output
                if output:
                    self.insert('end', output, 'output')
                self.mark_set('input', 'end')
                self.see('end')
                if not res and self.compare('insert linestart', '>', 'insert'):
                    self.insert('insert', '\n')
                self.prompt(res)
                if auto_indent and lines:
                    # insert indentation similar to previous lines
                    indent = re.search(r'^( )*', lines[-1]).group()
                    line = lines[-1].strip()
                    if line and line[-1] == ':':
                        indent = indent + '    '
                    self.insert('insert', indent)
                self.see('end')
                if res:
                    self.mark_set('input', index)
                    self._console.resetbuffer()  # clear buffer since the whole command will be retrieved from the text widget
                elif lines:
                    self.history.append(lines)  # add commands to history
                    self._hist_item = len(self.history)
            out.close()
            err.close()
        else:
            self.insert('insert', '\n')
            self.prompt()

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
    text = ScrolledText(root, state="normal", height=28, width=400, wrap="word", pady=2, padx=3, undo=True)
    text.pack(expand=True, fill="both", side=TOP)
    text.focus_set()

    # First Shell
    tabControl1 = ttk.Notebook(root)
    textEditor1 = ttk.Frame(tabControl1)
    tabControl1.add(panedWindow, text='Shell')
    tabControl1.pack(expand=True, fill="both", side=TOP)

    # Second Text
    font1 = Font(family="JetBrains Mono")
    text1 = TextConsole(root, state="normal", height=13, width=400, wrap="word", pady=2, padx=3, undo=True)
    text1.pack()
    text1.focus_set()

    # Second ListBox
    right_list = tk.Listbox(tabControl1)
    right_list.pack(side=tk.TOP)
    panedWindow.add(tabControl1)
    panedWindow.pack(fill=tk.BOTH)

    # Syntax Highlighting
    newSyntax = ic.ColorDelegator()
    newSyntax.idprog = re.compile(r'\s+(\w+)', re.S)
    newSyntax.tagdefs['CLASSDEF'] = {'foreground': '#BF42F5', 'background': '#FFFFFF'}
    newSyntax.tagdefs['MYGROUP'] = {'foreground': '#E07634', 'background': '#FFFFFF'}
    newSyntax.tagdefs['COMMENT'] = {'foreground': 'Green', 'background': '#FFFFFF'}
    newSyntax.tagdefs['KEYWORD'] = {'foreground': '#00507F', 'background': '#FFFFFF'}
    newSyntax.tagdefs['BUILTIN'] = {'foreground': '#CCBA18', 'background': '#FFFFFF'}
    newSyntax.tagdefs['STRING'] = {'foreground': '#A65E17', 'background': '#FFFFFF'}
    newSyntax.tagdefs['DEFINITION'] = {'foreground': '#188EA3', 'background': '#FFFFFF'}
    ip.Percolator(text).insertfilter(newSyntax)

    # Menubar
    menubar = Menu(root)
    file_menu.main(root, text, menubar)
    edit_menu.main(root, text, menubar)
    format_menu.main(root, text, menubar)
    help_menu.main(root, text, menubar)

    # Code Output
    code_output = Text(height=8.75)
    code_output.pack()

    # Run the Window
    root.mainloop()