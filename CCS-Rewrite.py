import tkinter as tk
import json
import datetime as dt
from tkinter import messagebox
from tkinter import font
from PIL import Image, ImageTk

from files.config.fonts import pf
from files.config.CN_EN import eng_chn_li
from files.hash_PSD import hash
from files.config.parameters import params

eng_chn = params.eng_chn

f1 = open('files\\YQ_DataBase.json', 'r')
ms = json.loads(f1.read())
f1.close()
person = {}      # 当前登录用户信息
s_n = 4          # 剩余登录尝试次数
d = eng_chn_li[2][eng_chn]    # 密码显示状态
d2 = eng_chn_li[2][eng_chn]   # 密码显示状态

class CCS:
    def __init__(self):
        self.win = tk.Tk()
        self.win.geometry('320x370+120+120')
        self.win.title(eng_chn_li[0][eng_chn])
        self.win.config(background='light cyan')
        self.win.resizable(False,False)
        self.win.iconbitmap('images\\云棋AI.ico')

        self.gui()
    def gui(self):
        self.img = Image.open(eng_chn_li[1][eng_chn])
        self.img2 = ImageTk.PhotoImage(self.img)
        self.bg1 = tk.Label(self.win, image=self.img2, bg='light cyan')
        self.bg1.place(x=-1, y=-3)
        self.ask = tk.Label(self.win, text=eng_chn_li[5][eng_chn],bg='light cyan', font=font.Font(family=pf,size=15))
        self.ask.place(x=20, y=80)
        self.name = tk.Label(self.win, text=eng_chn_li[6][eng_chn],bg='light cyan', font=font.Font(family=pf,size=16))
        self.name.place(x=20, y=130)
        self.name2 = tk.Entry(self.win,width=20,font=font.Font(family=pf,size=16))
        self.name2.place(x=20, y=170)
        self.name2.focus()
        self.name2.bind('<Return>',lambda e:self.cstart())
        self.name = tk.Label(self.win, text=eng_chn_li[7][eng_chn],bg='light cyan', font=font.Font(family=pf,size=16))
        self.name.place(x=20, y=210)
        self.mm= tk.Entry(self.win,width=15, font=font.Font(family=pf,size=16), show='•')
        self.mm.place(x=20, y=250)
        self.mm.bind('<Return>',lambda e:self.cstart())
        self.de = tk.Button(self.win, command=self.change, width=5, text=eng_chn_li[2][eng_chn], font=font.Font(family=pf,size=10),activebackground='whitesmoke',bg='whitesmoke')
        self.de.place(x=200, y=250)
        self.get = tk.Button(self.win, command=self.cstart, width=10, text=eng_chn_li[8][eng_chn], font=font.Font(family=pf,size=15),activebackground='whitesmoke',bg='whitesmoke')
        self.get.place(x=35, y=290)
        self.get2 = tk.Button(self.win, command=self.make_new, width=10,height=1, text=eng_chn_li[9][eng_chn], font=font.Font(family=pf,size=15),activebackground='whitesmoke',bg='whitesmoke')
        self.get2.place(x=155, y=290)
        self.about_me = tk.Label(self.win, text='◎'+eng_chn_li[0][eng_chn],bg='light cyan',fg='grey', font=font.Font(family=pf,size=9))
        self.about_me.place(x=5, y=340)
        self.chg = tk.Button(self.win, command=self.eng_chn_chg, width=8, text=eng_chn_li[114][eng_chn], font=font.Font(family=pf,size=10),activebackground='whitesmoke',bg='whitesmoke')
        self.chg.place(x=250, y=345)
    def change(self):
        global d
        if d == eng_chn_li[2][eng_chn]:
            d = eng_chn_li[3][eng_chn]
            self.de.config(text=d)
            self.mm.config(show='')
        elif d == eng_chn_li[3][eng_chn]:
            d = eng_chn_li[2][eng_chn]
            self.de.config(text=d)
            self.mm.config(show='•')
    def cstart(self):
        global s_n, ms, person
        if self.name2.get() != '' and self.mm.get() != '':
            if self.name2.get() in ms.keys():
                sal, has = ms[self.name2.get()]['password'].split(':')
                if hash(self.mm.get(), sal)[1] == has:
                    person = ms[self.name2.get()]
                    if 'game_num' not in person:
                        person['game_num'] = 0
                    if 'lose_num' not in person:
                        person['lose_num'] = 0
                    if 'beat_hard' not in person:
                        person['beat_hard'] = 0
                    if 'online_num' not in person:
                        person['online_num'] = 0
                    if 'cj_win' not in person:
                        person['cj_win'] = 0
                    if 'cj_done' not in person:
                        person['cj_done'] = []
                    if 'lian_win_max' not in person:
                        person['lian_win_max'] = 0
                    if 'lian_win_now' not in person:
                        person['lian_win_now'] = 0
                    def run_Main():
                        try:
                            params.person = person
                            self.win.destroy()
                            from files.core import main_ui_win
                            main_ui_win()
                        except OSError as e:
                            messagebox.showerror("启动失败", f"错误：{str(e)}")
                    run_Main()
                else:
                    if s_n != 1:
                        s_n -= 1
                        messagebox.showerror(eng_chn_li[14][eng_chn], eng_chn_li[21][eng_chn]+str(s_n)+eng_chn_li[22][eng_chn])
                    else:
                        self.win.destroy()
            else:
                messagebox.showinfo(eng_chn_li[14][eng_chn], eng_chn_li[20][eng_chn])
        else:
            messagebox.showwarning(eng_chn_li[14][eng_chn], eng_chn_li[17][eng_chn])
    def make_new(self):
        win4 = tk.Toplevel()
        win4.geometry('320x390+100+100')
        win4.title(eng_chn_li[12][eng_chn])
        win4.configure(bg='light cyan')
        win4.resizable(False,False)
        win4.iconbitmap('images\\云棋AI.ico')

        img = Image.open(eng_chn_li[13][eng_chn])
        img2 = ImageTk.PhotoImage(img)
        bg1 = tk.Label(win4, image=img2, bg='light cyan')
        bg1.place(x=-1, y=-3)
        def change1():
            global d
            if d == eng_chn_li[2][eng_chn]:
                d = eng_chn_li[3][eng_chn]
                de1.config(text=d)
                mm.config(show='')
            elif d == eng_chn_li[3][eng_chn]:
                d = eng_chn_li[2][eng_chn]
                de1.config(text=d)
                mm.config(show='•')
        def change2():
            global d2
            if d2 == eng_chn_li[2][eng_chn]:
                d2 = eng_chn_li[3][eng_chn]
                de2.config(text=d2)
                mm2.config(show='')
            elif d2 == eng_chn_li[3][eng_chn]:
                d2 = eng_chn_li[2][eng_chn]
                de2.config(text=d2)
                mm2.config(show='•')
        def make_new():
            global ms,rfp
            if not(name2.get() == '' or mm.get() == '' or mm2.get() == ''):
                if name2.get() not in ms.keys():
                    if mm.get() == mm2.get():
                        if mm.get().isnumeric() or mm.get().isalpha() or len(mm.get()) < 5 or not mm.get().isalnum():
                            messagebox.showwarning(eng_chn_li[14][eng_chn], eng_chn_li[19][eng_chn])
                        else:
                            f1 = open('files\\YQ_DataBase.json', 'w')
                            t1, t2 = str(dt.datetime.now())[:10], str(dt.datetime.now())[-6:]
                            t3 = ''.join(t1.split('-'))
                            t4 = "YH"+t3+t2
                            sal, pasw = hash(mm.get())
                            ms[name2.get()] = {
                                'photo':'',
                                'name':name2.get(),
                                'password':f'{sal}:{pasw}',
                                'password_length':len(mm.get()),
                                'ID':t4,
                                'win_num':0,
                                'YH_number':0,
                                'level':1,
                                'english_type':eng_chn,
                                'connect_list':[],
                                'game_num':0,
                                'lose_num':0,
                                'beat_hard':0,
                                'online_num':0,
                                'cj_win':0,
                                'cj_done':[],
                                'lian_win_max':0,
                                'lian_win_now':0,
                            }
                            f1.writelines(json.dumps(ms))
                            with open('files\\history.json', 'r') as f3:
                                rrs = json.loads(f3.read())
                            rrs[name2.get()] = {}
                            with open('files\\history.json', 'w') as f4:
                                f4.write(json.dumps(rrs))
                            messagebox.showinfo(eng_chn_li[14][eng_chn], eng_chn_li[18][eng_chn])
                            win4.destroy()
                            f1.close()
                    else:
                        messagebox.showinfo(eng_chn_li[14][eng_chn], eng_chn_li[15][eng_chn])
                else:
                    messagebox.showinfo(eng_chn_li[14][eng_chn], eng_chn_li[16][eng_chn])
            else:
                messagebox.showwarning(eng_chn_li[14][eng_chn], eng_chn_li[17][eng_chn])
        name = tk.Label(win4, text=eng_chn_li[6][eng_chn],bg='light cyan', font=font.Font(family=pf,size=16))
        name.place(x=25, y=80)
        name2 = tk.Entry(win4,width=20,font=font.Font(family=pf,size=16))
        name2.place(x=25, y=120)
        name = tk.Label(win4, text=eng_chn_li[7][eng_chn],bg='light cyan', font=font.Font(family=pf,size=16))
        name.place(x=25, y=160)
        mm = tk.Entry(win4,width=15, font=font.Font(family=pf,size=16), show='•')
        mm.place(x=25, y=200)
        name = tk.Label(win4, text=eng_chn_li[10][eng_chn],bg='light cyan', font=font.Font(family=pf,size=16))
        name.place(x=25, y=240)
        mm2 = tk.Entry(win4,width=15, font=font.Font(family=pf,size=16), show='•')
        mm2.place(x=25, y=280)
        de1 = tk.Button(win4, command=change1, width=5, text=eng_chn_li[2][eng_chn], font=font.Font(family=pf,size=10),activebackground='whitesmoke',bg='whitesmoke')
        de1.place(x=205, y=200)
        de2 = tk.Button(win4, command=change2, width=5, text=eng_chn_li[2][eng_chn], font=font.Font(family=pf,size=10),activebackground='whitesmoke',bg='whitesmoke')
        de2.place(x=205, y=280)
        get = tk.Button(win4, command=make_new, width=20, text=eng_chn_li[11][eng_chn], font=font.Font(family=pf,size=15),activebackground='whitesmoke',bg='whitesmoke')
        get.place(x=55, y=320)
        about_me = tk.Label(win4, text='◎'+eng_chn_li[0][eng_chn],bg='light cyan',fg='grey', font=font.Font(family=pf,size=9))
        about_me.place(x=5, y=365)
        win4.mainloop()
    def eng_chn_chg(self):
        global eng_chn, d, d2
        if eng_chn == 0:
            eng_chn = 1
            params.eng_chn = 1
        elif eng_chn == 1:
            eng_chn = 0
            params.eng_chn = 0
        d = eng_chn_li[2][eng_chn]
        d2 = eng_chn_li[2][eng_chn]
        self.win.destroy()
        CCS().run()

    def run(self):
        self.win.mainloop()

if __name__ == '__main__':
    CCS().run()