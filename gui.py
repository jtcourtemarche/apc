import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

root = tk.Tk()

root.title = 'APC Scanner'
root.geometry('800x600')
root.resizable(0, 0)

frame = tk.Frame(master=root, bg='#393D49')
frame.pack(fill=tk.BOTH, expand=1)

# Name schema:
# 	{ name }_{ tkinter type }	

main_label = tk.Label(frame, text='APC Scanner').grid(row=0, column=0)
links_text = ScrolledText(frame).grid(row=1, column=0)
out_listbox = tk.Listbox(frame).grid(row=0, column=1)

root.mainloop()