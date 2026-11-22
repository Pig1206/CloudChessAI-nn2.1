import tkinter as tk
from tkinter import font
from os.path import join as jp
from PIL import Image, ImageTk

from files.config.parameters import params
from files.config.CN_EN import eng_chn_li
from files.config.fonts import ph, pz
from files.config.paths_parameters import images_path

eng_chn = params.eng_chn
person = params.person


class NavigationBar():
    def __init__(self, parent):
        self.parent = parent

        self.de_buttons = {}
        self.fs = tk.Canvas(self.parent, width=500, height=4, bg='black', highlightbackground='light cyan')
        self.fs.place(x=-5, y=38 + 65)

        self.de_buttons[1] = tk.Button(self.parent, width=9, height=2, text=eng_chn_li[120][eng_chn],
                                       font=font.Font(family=ph, size=10), activebackground='whitesmoke',
                                       bg='whitesmoke')
        self.de_buttons[1].place(x=0, y=70)
        self.de_buttons[2] = tk.Button(self.parent, width=9, height=2, text=eng_chn_li[121][eng_chn],
                                       font=font.Font(family=ph, size=10), activebackground='deepskyblue',
                                       bg='deepskyblue')
        self.de_buttons[2].place(x=73, y=70)
        self.de_buttons[3] = tk.Button(self.parent, width=9, height=2, text=eng_chn_li[122][eng_chn],
                                       font=font.Font(family=ph, size=10), activebackground='deepskyblue',
                                       bg='deepskyblue')
        self.de_buttons[3].place(x=73 * 2, y=70)
        self.de_buttons[4] = tk.Button(self.parent, width=9, height=2, text=eng_chn_li[123][eng_chn],
                                       font=font.Font(family=ph, size=10), activebackground='deepskyblue',
                                       bg='deepskyblue')
        self.de_buttons[4].place(x=73 * 3, y=70)
        self.de_buttons[5] = tk.Button(self.parent, width=9, height=2, text=eng_chn_li[124][eng_chn],
                                       font=font.Font(family=ph, size=10), activebackground='deepskyblue',
                                       bg='deepskyblue')
        self.de_buttons[5].place(x=73 * 4, y=70)

        self.param_btn = tk.Button(self.parent, text="参数调整", width=10, font=font.Font(family=pz, size=10),
                                   activebackground='whitesmoke', bg='whitesmoke')
        self.param_btn.place(x=250, y=5)

        self.bg_img = Image.open(jp(images_path, '云棋AI-BG1.png'))
        self.crop_bg = self.bg_img.crop((200, 40, 320, 60))
        self.crop_bg_tk = ImageTk.PhotoImage(self.crop_bg)

        self.cv = tk.Canvas(self.parent, width=120, height=20, highlightthickness=0, bd=0)
        self.cv.place(x=200, y=40)
        self.cv.create_image(0, 0, image=self.crop_bg_tk, anchor='nw')
        self.cv.image = self.crop_bg_tk
        self.color_list = ['#2E8B57', '#800080', '#FFC0CB', '#4169E1', '#CD5C5C', '#00FF00', '#FFD700', '#7B68EE',
                           '#C0C0C0', '#00FFFF']

        def choose(level):
            if level < 11:
                return '⬆'
            elif level < 21:
                return '◆'
            else:
                return '★'

        self.cv.create_text(60, 10, text=choose(person['level']) + 'Lv.' + str(person['level']),
                            fill=self.color_list[(person['level'] - 1) % 10],
                            font=font.Font(family=pz, size=14, weight='bold'))

    def set_nbs(self, func):
        for i in range(1, 6):
            self.de_buttons[i].config(command=lambda arg=i: func(arg))

    def set_param_command(self, func):
        self.param_btn.config(command=func)