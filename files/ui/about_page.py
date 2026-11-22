import tkinter as tk
from tkinter import font, messagebox
from PIL import Image, ImageTk
import os

from files.config.parameters import params
from files.config.CN_EN import eng_chn_li
from files.config.fonts import pf

eng_chn = params.eng_chn

class About():
    def __init__(self, parent):
        self.parent = parent

        self.abo_labels = {}
        y = 120
        al = eng_chn_li[119][eng_chn]
        al2 = al.split('\n')
        for i in range(11):
            self.abo_labels[i] = tk.Label(self.parent, text=al2[i], bg='light cyan', font=font.Font(family=pf, size=15))
            self.abo_labels[i].place(x=10, y=y)
            y += 25

        def function1(arg):
            messagebox.showinfo(eng_chn_li[115][eng_chn],
                                '1.李忠良，陈莉\n2.宫城老师，孙玉燕老师\n3.CSDN社区\n4.JetBrain\n5.deepseek深度求索')

        def function2(arg):
            messagebox.showinfo(eng_chn_li[116][eng_chn], eng_chn_li[117][eng_chn])

        self.abo_labels[9].bind('<Double-Button-1>', function1)
        self.abo_labels[10].bind('<Double-Button-1>', function2)

        def close():
            self.parent.destroy()

        self.abo_labels[11] = tk.Label(self.parent, text=eng_chn_li[118][eng_chn], bg='light cyan',
                                  font=font.Font(family=pf, size=15), fg='red')
        self.abo_labels[11].place(x=10, y=400)
        #12 , command=re_start
        self.abo_labels[12] = tk.Button(self.parent, width=10, text=eng_chn_li[79][eng_chn],
                                   font=font.Font(family=pf, size=15), activebackground='whitesmoke', bg='whitesmoke')
        self.abo_labels[12].place(x=50, y=435)
        self.abo_labels[13] = tk.Button(self.parent, command=close, width=10, text=eng_chn_li[80][eng_chn],
                                   font=font.Font(family=pf, size=15), activebackground='whitesmoke', bg='whitesmoke')
        self.abo_labels[13].place(x=200, y=435)
        global img, img2
        img = Image.open(os.path.abspath('images\\山西广寰图片.png'))
        img2 = ImageTk.PhotoImage(img)
        self.abo_labels[14] = tk.Label(self.parent, image=img2, bg='light cyan')
        self.abo_labels[14].place(x=250, y=112)