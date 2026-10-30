import tkinter as tk
from tkinter import messagebox
from os.path import join as jp
from PIL import Image, ImageTk
import random as rd
import json, threading
import datetime

from files.config.CN_EN import eng_chn_li
from files.config.parameters import params
from files.config.paths_parameters import images_path

from files.functions.check_win import check
from files.functions.apply_game_result import apply_game_result
from files.functions.ccs_mnn import CCScore

from files.ui.chess_board import ChessBoard
from files.ui.navigation_bar import NavigationBar
from files.ui.myself_page import Myself
from files.ui.about_page import About
from files.ui.param_adjust import ParamAdjustWindow

eng_chn = params.eng_chn
person = params.person
play_state = params.play_state
q = params.q
play_num = params.play_num
num = params.num
multiplayer_mode = params.multiplayer_mode
up_state = params.up_state


class main_ui_win():
    def __init__(self):
        self.win3 = tk.Tk()
        self.win3.geometry('360x550+100+100')
        self.win3.title(eng_chn_li[0][eng_chn])
        self.win3.configure(bg='light cyan')
        self.win3.resizable(False, False)
        self.win3.iconbitmap(jp(images_path, '云棋AI.ico'))

        if person and 'name' in person:
            params.load_user_ai_params(person['name'])

        self.win3.update()
        self.win3.after(0, self.draw)

        self.win3.mainloop()

    def draw(self):
        self.img = Image.open(jp(images_path, '云棋AI-BG1.png'))
        self.img2 = ImageTk.PhotoImage(self.img)
        self.bg1 = tk.Label(self.win3, image=self.img2)
        self.bg1.place(x=-1, y=-3)

        self.cb = ChessBoard(self.win3)
        self.ngb = NavigationBar(self.win3)

        self.cb.set_start_command(self.start_game)
        self.cb.set_board_command(self.step_move)
        self.ngb.set_nbs(self.change_nums)

        self.ngb.set_param_command(self.adjust_params)

        self.cb.cn_buttons[123].config(state='disabled')
        self.win3.after(0, self.start_loading)

    def adjust_params(self):
        ParamAdjustWindow(self.win3)

    def start_loading(self):
        threading.Thread(target=self.load_models, daemon=True).start()

    def load_models(self):
        try:
            self.win3.update_idletasks()
            from files.functions.CCS_CoreNetWork import _load_models
            _load_models()
            self.cb.cn_buttons[123].config(state='normal')
        except Exception as e:
            tk.messagebox.showerror("加载失败", str(e))

    def start_game(self):
        global play_state, q, play_num, num
        for i in range(1, 122):
            self.cb.cn_buttons[i].config(text='')
            q = [[0 for _ in range(11)] for _ in range(11)]
        play_state = 1
        params.play_state = 1
        num = 0
        params.num = 0
        if play_num == 2:
            num = rd.choice([[5, 5], [4, 4], [4, 6], [6, 4], [6, 6], [5, 5], [5, 5], [5, 5]])
            q[num[0]][num[1]] = 2
            params.q[num[0]][num[1]] = 2
            self.cb.cn_buttons[num[0] * 11 + num[1] + 1].config(text='○')
        if play_num == 3 and multiplayer_mode == 2:
            self.cb.cn_buttons[122].config(text=eng_chn_li[105][eng_chn])

    def step_move(self, n):
        global num, play_num, play_state, q, num2_state, person, connection, multiplayer_mode

        if play_state == 1:
            if self.cb.cn_buttons[n]['text'] != '○' and self.cb.cn_buttons[n]['text'] != '●':
                if play_num == 1 or play_num == 2:
                    ns = n - 1
                    row = ns // 11
                    col = ns % 11
                    q[row][col] = 1
                    self.cb.cn_buttons[n].config(text='●')
                    if check(q) == 1:
                        messagebox.showinfo(eng_chn_li[111][eng_chn], eng_chn_li[106][eng_chn])
                        play_state = 0
                        num2_state = 0
                        f1 = open('files_old\\YQ_DataBase.json', 'r')
                        rt = json.loads(f1.read())
                        f1.close()
                        rt[person['name']]['YH_number'] = rt[person['name']].get('YH_number', 0) + 5
                        rt[person['name']]['level'] = int(rt[person['name']]['YH_number']) // 100 + 1
                        with open('files\\YQ_DataBase.json', 'w') as f2:
                            f2.writelines(json.dumps(rt))
                        person['YH_number'] = rt[person['name']]['YH_number']
                        person['level'] = rt[person['name']]['level']
                        apply_game_result(True, is_online=False, is_hard=True)
                        with open('files\\history.json', 'r') as f3:
                            rrs = json.loads(f3.read())
                        rrs[person['name']].update({str(q): ['me', str(datetime.datetime.now())]})
                        with open('files\\history.json', 'w') as f4:
                            f4.write(json.dumps(rrs))

                    if play_state == 1:
                        for i in range(1, 122):
                            self.cb.cn_buttons[i].config(state='disabled')

                        def ai_move():
                            global q, play_state

                            p = params.ai_params
                            loc = CCScore(
                                q,
                                difficulty=p['n_sim'],
                                c_puct=p['c_puct'],
                                temperature=p['temp'],
                                n_threads=p['n_threads'],
                                sigma=p.get('sigma', 0.001),
                                username=person['name'] if p['use_opp_model'] else None,
                                opp_weight=p['opp_weight']
                            ).find_best_move()

                            q[loc[1]][loc[0]] = 2

                            def update_ui():
                                self.cb.cn_buttons[loc[1] * 11 + loc[0] + 1].config(text='○')

                                if check(q) == 2:
                                    messagebox.showinfo(eng_chn_li[111][eng_chn], eng_chn_li[107][eng_chn])
                                    apply_game_result(False)
                                    with open('files\\history.json', 'r') as f3:
                                        rrs = json.loads(f3.read())
                                    rrs[person['name']].update({str(q): ['AI', str(datetime.datetime.now())]})
                                    with open('files\\history.json', 'w') as f4:
                                        f4.write(json.dumps(rrs))

                                for i in range(1, 122):
                                    self.cb.cn_buttons[i].config(state='normal')

                            self.win3.after(0, update_ui)

                        threading.Thread(target=ai_move, daemon=True).start()

    def change_nums(self, n):
        global play_num, up_state
        play_num = n
        for i in range(1, 6):
            if i != n:
                self.ngb.de_buttons[i].config(activebackground='deepskyblue', bg='deepskyblue')
        self.ngb.de_buttons[n].config(activebackground='whitesmoke', bg='whitesmoke')
        if n <= 3:
            if up_state != 0:
                if up_state == 1:
                    for i in range(26): self.mp.d_labels[i].destroy()
                elif up_state == 2:
                    for i in range(15): self.ab.abo_labels[i].destroy()
                up_state = 0
                params.up_state = 0
                self.cb = ChessBoard(self.win3)
                self.cb.set_start_command(self.start_game)
                self.cb.set_board_command(self.step_move)
            if n == 1: self.cb.change_text(eng_chn_li[24][eng_chn])
            if n == 2: self.cb.change_text(eng_chn_li[25][eng_chn])
            if n == 3: self.cb.change_text(eng_chn_li[26][eng_chn])
        elif n == 4:
            if not (up_state == 1):
                if up_state == 0:
                    for i in range(1, 124): self.cb.cn_buttons[i].destroy()
                elif up_state == 2:
                    for i in range(15): self.ab.abo_labels[i].destroy()
                up_state = 1
                params.up_state = 1
                self.mp = Myself(self.win3)
        elif n == 5:
            if up_state != 2:
                if up_state == 0:
                    for i in range(1, 124): self.cb.cn_buttons[i].destroy()
                if up_state == 1:
                    for i in range(26): self.mp.d_labels[i].destroy()
                up_state = 2
            self.ab = About(self.win3)


if __name__ == '__main__':
    main_ui_win()