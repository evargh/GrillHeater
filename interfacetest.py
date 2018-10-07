from Tkinter import *

import time

root = Tk()
root.geometry('500x500')

rows = 0
while rows < 50:
    root.rowconfigure(rows, weight=1)
    root.columnconfigure(rows,weight=1)
    rows+=1

target = IntVar()
target.set(100)
motSpeed = IntVar()
motSpeed.set(100)
runt = IntVar()
runt.set(10)
endt = IntVar()
endt.set(10)

temp = StringVar()
temp.set('Temp: 0')
labbelTemp = Label(root, textvariable=temp, font=("Helvetica",18))
labbelTemp.grid(row=10,column=10)
delts = StringVar()
delts.set('Delta: 0')
labbelDelt = Label(root, textvariable=delts, font=("Helvetica",18))
labbelDelt.grid(row=10,column=30)

tempEnt = Entry(root)
tempEnt.grid(row=30,column=10)
submit1 = Button(root, text="Target Temperature", width=15, command=lambda: setTemp(tempEnt.get()))
submit1.grid(row=30,column=30)
tempEnt.insert(0,"100")

labbelTitle = Label(root, text="Raspi Smoke & Grill", font=("Helvetica",30))
labbelTitle.grid(row=40,column=30)

def setTemp(nice):
    target.set(int(nice))
