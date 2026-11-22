import tkinter as tk
from tkinter import font
from PIL import ImageTk

from files.config.parameters import params
from files.config.CN_EN import eng_chn_li
from files.config.fonts import pf
from files.functions.make_circle_img import make_circle_img

eng_chn = params.eng_chn
person = params.person

class Myself():
    def __init__(self, parent):
        self.parent = parent

        self.d_labels = {}
        str_list = eng_chn_li[27][eng_chn].split()
        lir = ['name', 'YH_number', 'ID', 'password', 'level', 'win_num']
        for i in range(13, 20):
            self.d_labels[i] = tk.Canvas(self.parent, width=500, height=1, bd=0, bg='light gray', highlightbackground='light cyan')
            self.d_labels[i].place(x=0, y=150 + (i - 13) * 45)

        # 显示圆形头像
        photo_path = person.get('photo', '')
        if not photo_path:
            photo_path = 'images\\Sphotograph.png'
        cir_img = make_circle_img(photo_path, (35, 35))
        photo_tk = ImageTk.PhotoImage(cir_img)
        self.d_labels[25] = tk.Label(self.parent, image=photo_tk, bg='light cyan')
        self.d_labels[25].image = photo_tk
        self.d_labels[25].place(x=190, y=110)

        for i in range(7):
            self.d_labels[i] = tk.Label(self.parent, text=str_list[i], font=font.Font(family=pf, size=15), bg='light cyan')
            self.d_labels[i].place(x=20, y=120 + i * 45)
        for i in range(7, 13):
            if lir[i - 7] == 'password':
                pw_show = '*' * person.get('password_length', 8)
                self.d_labels[i] = tk.Label(self.parent, text=pw_show, font=font.Font(family=pf, size=15), bg='light cyan')
            elif lir[i - 7] == 'level':
                self.d_labels[i] = tk.Label(self.parent, text='Lv.' + str(person[lir[i - 7]]), font=font.Font(family=pf, size=15),
                                       bg='light cyan')
            else:
                self.d_labels[i] = tk.Label(self.parent, text=person[lir[i - 7]], font=font.Font(family=pf, size=15),
                                       bg='light cyan')
            self.d_labels[i].place(x=195, y=165 + (i - 7) * 45)
        #20 , command=account_mg
        self.d_labels[20] = tk.Button(self.parent, text=eng_chn_li[28][eng_chn], width=13, font=font.Font(family=pf, size=15),
                                 activebackground='whitesmoke', bg='whitesmoke')
        self.d_labels[20].place(x=30, y=435)
        #21 , command=show_cj_list
        self.d_labels[21] = tk.Button(self.parent, text=eng_chn_li[62][eng_chn], width=13,
                                 font=font.Font(family=pf, size=15), activebackground='whitesmoke', bg='whitesmoke')
        self.d_labels[21].place(x=190, y=435)
        self.d_labels[22] = tk.Canvas(self.parent, width=1, height=310, bd=0, bg='light gray', highlightbackground='light cyan')
        self.d_labels[22].place(x=130, y=110)
        #23 , command=history_info
        self.d_labels[23] = tk.Button(self.parent, text=eng_chn_li[47][eng_chn], width=13,
                                 font=font.Font(family=pf, size=15), activebackground='whitesmoke', bg='whitesmoke')
        self.d_labels[23].place(x=30, y=475)
        #24 , command=canju_challenge
        self.d_labels[24] = tk.Button(self.parent, text=eng_chn_li[64][eng_chn], width=13,
                                 font=font.Font(family=pf, size=15), activebackground='whitesmoke', bg='whitesmoke')
        self.d_labels[24].place(x=190, y=475)
