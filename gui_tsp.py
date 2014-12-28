__author__ = 'sotiris'
#! /usr/bin/env python
# -*- coding: utf-8 -*-


"""
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from Tkinter import *
import Tkinter, Tkconstants, tkFileDialog
import ttk
from parser import *

root = Tk()
root.title("TSP Solver")
root.geometry("1024x768")
def openFile():
    filename = tkFileDialog.askopenfilename()
    produce_final(filename)

# entry_1 = Entry(root)
# entry_2 = Entry(root)

# entry_1.grid(row = 0, column = 0)
# entry_2.grid(row = 1, column = 1)

# def printName(event):
#     print "Hello Sam"

# topFrame = Frame(root)
# topFrame.pack()
# bottomFrame = Frame(root)
# bottomFrame.pack(side = BOTTOM)
# theLabel = ttk.Label(root, text = 'test again test')
# theLabel.grid(row = 0, column = 1, sticky = W)
# c = Checkbutton(root, text = "keep me in man")
# c.grid(columnspan = 2)

button1 = ttk.Button(root, text = 'test', padding = 5, command = openFile)
# button1.bind("<Button-1>", printName)
# button2 = ttk.Button(topFrame, text = 'test')
# button3 = Button(root, text = 'test')
# button4 = ttk.Button(bottomFrame, text = 'test')

button1.grid(row = 0, column = 1, sticky = W)
# button2.pack(side = LEFT)
# button3.pack(fill = X)
# button4.pack(side = LEFT)


root.mainloop()