"""联机方式选择框 (适配 Cloudflare Worker 版)"""

import tkinter as tk
from tkinter import font
from tkinter import messagebox

from files.config.parameters import params
from files.config.CN_EN import eng_chn_li
from files.config.fonts import pz

eng_chn = params.eng_chn

W, H = 300, 250


class NetDialog():
    def __init__(self, parent, on_done):
        self.on_done = on_done
        self.mode = 0

        self.win = tk.Toplevel(parent)
        self.win.title(eng_chn_li[125][eng_chn])
        self.win.geometry(f'{W}x{H}+120+140')
        self.win.configure(bg='light cyan')
        self.win.resizable(False, False)
        self.win.protocol('WM_DELETE_WINDOW', self.destroy)
        try:
            self.win.transient(parent)
            self.win.grab_set()
        except Exception:
            pass

        self.body = tk.Frame(self.win, bg='light cyan')
        self.body.place(x=0, y=0, width=W, height=H)

        self.room_entry = None
        self.pw_entry = None

        self.show_menu()

    def show_menu(self):
        self._clear()
        tk.Label(self.body, text=eng_chn_li[125][eng_chn], bg='light cyan',
                 font=font.Font(family=pz, size=14)).place(x=20, y=10)

        self._button(eng_chn_li[126][eng_chn], 48, self.choose_local)
        # 统一为一个入口：进入联机房间
        self._button("进入联机房间", 93, lambda: self.show_form(1))
        self._button(eng_chn_li[129][eng_chn], 188, self.destroy)

    def choose_local(self):
        self.destroy()
        # mode = 0 代表线下双人
        self.on_done(0, '', '')

    def show_form(self, mode):
        # 这里 mode 传 1 或 2 都可以，我们实际上靠 Worker 分配主机/客机
        self.mode = mode
        self._clear()

        title = "联机房间"
        tk.Label(self.body, text=title, bg='light cyan',
                 font=font.Font(family=pz, size=14)).place(x=20, y=10)

        tk.Label(self.body, text=eng_chn_li[130][eng_chn], bg='light cyan',
                 font=font.Font(family=pz, size=11)).place(x=22, y=53)
        self.room_entry = tk.Entry(self.body, width=17, font=font.Font(family=pz, size=11))
        self.room_entry.place(x=95, y=50)

        tk.Label(self.body, text=eng_chn_li[131][eng_chn], bg='light cyan',
                 font=font.Font(family=pz, size=11)).place(x=22, y=93)
        self.pw_entry = tk.Entry(self.body, width=17, show='*',
                                 font=font.Font(family=pz, size=11))
        self.pw_entry.place(x=95, y=90)

        hint = "填入相同房间号即可匹配"
        tk.Label(self.body, text=hint, bg='light cyan', fg='gray',
                 font=font.Font(family=pz, size=9)).place(x=95, y=116)

        tk.Button(self.body, text=eng_chn_li[140][eng_chn], width=8,
                  font=font.Font(family=pz, size=11), bg='deepskyblue',
                  command=self.submit).place(x=52, y=160)
        tk.Button(self.body, text=eng_chn_li[129][eng_chn], width=8,
                  font=font.Font(family=pz, size=11), bg='whitesmoke',
                  command=self.show_menu).place(x=160, y=160)

        self.room_entry.focus_set()

    def submit(self):
        room = self.room_entry.get().strip()
        if not room or ' ' in room:
            messagebox.showwarning(eng_chn_li[112][eng_chn], eng_chn_li[133][eng_chn])
            return
        pw = self.pw_entry.get()

        # mode 我们固定传 1 作为联机标识，由 core.py 去处理具体的先后手逻辑
        mode = 1
        self.destroy()
        self.on_done(mode, room, pw)

    def _button(self, text, y, command):
        tk.Button(self.body, text=text, width=18, font=font.Font(family=pz, size=12),
                  bg='deepskyblue', command=command).place(x=52, y=y)

    def _clear(self):
        for w in self.body.winfo_children():
            w.destroy()

    def destroy(self):
        try:
            self.win.grab_release()
        except Exception:
            pass
        try:
            self.win.destroy()
        except Exception:
            pass