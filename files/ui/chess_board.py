import tkinter as tk
from tkinter import font

from files.config.parameters import params
from files.config.CN_EN import eng_chn_li
from files.config.fonts import ph, pz

eng_chn = params.eng_chn


class ChessBoard():
    def __init__(self, parent):
        self.parent = parent
        self.__ft = font.Font(family=ph, size=13)

        rc_y = 150
        self.cn_buttons = {}
        for j in range(1, 12):
            for i in range(1, 12):
                self.cn_buttons[(j - 1) * 11 + i] = tk.Button(self.parent, width=2, height=1, activebackground='yellow',

                                                         font=self.__ft, bg='yellow')
                self.cn_buttons[(j - 1) * 11 + i].place(x=(i - 1) * 30 + 20, y=rc_y)
            rc_y += 30
        self.cn_buttons[122] = tk.Label(self.parent, text=eng_chn_li[24][eng_chn], font=font.Font(family=pz, size=13),
                                   bg='light cyan')
        self.cn_buttons[122].place(x=60, y=125)
        self.cn_buttons[123] = tk.Button(self.parent, width=10, height=1, text=eng_chn_li[23][eng_chn],
                                    font=font.Font(family=pz, size=15), activebackground='yellow', bg='yellow')
        self.cn_buttons[123].place(x=110, y=488)

    def set_board_command(self, func):
        for i in range(1, 122):
            self.cn_buttons[i].config(command=lambda arg=i: func(arg))

    def set_start_command(self, func2):
        self.cn_buttons[123].config(command=func2)

    def change_text(self, text):
        self.cn_buttons[122].config(text=text)