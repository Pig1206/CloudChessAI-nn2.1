import tkinter as tk
from tkinter import messagebox
from os.path import join as jp
from PIL import Image, ImageTk
import random as rd
import json, threading
import datetime
import queue

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
from files.ui.history_page import History

from files.ui.net_dialog import NetDialog
from files.network.ws_client import NetClient, NetError, ERR_AUTH, ERR_FULL, ERR_BAD_ROOM, ERR_NET

eng_chn = params.eng_chn
person = params.person
play_state = params.play_state
q = params.q
play_num = params.play_num
num = params.num
multiplayer_mode = params.multiplayer_mode
up_state = params.up_state

current_room_count = 0


class MainUIWindow():
    def __init__(self):
        self.win3 = tk.Tk()
        self.win3.geometry('360x550+100+100')
        self.win3.title(eng_chn_li[0][eng_chn])
        self.win3.configure(bg='light cyan')
        self.win3.resizable(False, False)
        self.win3.iconbitmap(jp(images_path, '云棋AI.ico'))

        self.net = None
        self.net_queue = queue.Queue()

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
        self.win3.after(80, self.poll_net)

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
        if play_num == 3:
            NetDialog(self.win3, self.on_net_choice)
            return
        self.close_net()
        self._begin_game()

    def _begin_game(self):
        global play_state, q, play_num, num, current_room_count
        current_room_count = 0
        for i in range(1, 122):
            self.cb.cn_buttons[i].config(text='', state='normal')
        q = [[0 for _ in range(11)] for _ in range(11)]
        params.q = q
        play_state = 1
        params.play_state = 1
        num = 0
        params.num = 0
        self.cb.cn_buttons[122].config(text=eng_chn_li[{1: 24, 2: 25, 3: 26}.get(play_num, 26)][eng_chn])

        if play_num == 2:
            num = rd.choice([[5, 5], [4, 4], [4, 6], [6, 4], [6, 6], [5, 5], [5, 5], [5, 5]])
            q[num[0]][num[1]] = 2
            params.q[num[0]][num[1]] = 2
            self.cb.cn_buttons[num[0] * 11 + num[1] + 1].config(text='○')

    def step_move(self, n):
        global num, play_num, play_state, q, num2_state, person, multiplayer_mode

        if play_num == 3:
            self.step_move_two(n)
            return

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
                        f1 = open('files\\YQ_DataBase.json', 'r')
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
                                target_btn = self.cb.cn_buttons[loc[1] * 11 + loc[0] + 1]
                                target_btn.config(text='○', fg='red')
                                self.win3.after(2000, lambda: target_btn.config(fg='black'))

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

    def _status(self, text):
        try:
            self.cb.cn_buttons[122].config(text=text)
        except Exception:
            pass

    def close_net(self):
        if self.net is not None:
            try:
                self.net.close()
            except Exception:
                pass
            self.net = None

    def on_net_choice(self, mode, room, pw):
        global multiplayer_mode, play_state, current_room_count
        multiplayer_mode = mode
        params.multiplayer_mode = mode
        current_room_count = 0
        self._begin_game()

        if mode == 0:
            self._status(eng_chn_li[122][eng_chn])
            return

        play_state = 0
        params.play_state = 0
        self._status(eng_chn_li[134][eng_chn])
        threading.Thread(target=self._connect_net, args=(mode, room, pw), daemon=True).start()

    def _connect_net(self, mode, room, pw):
        try:
            self.net = NetClient(on_event=self.on_net_event)
            self.net.connect(room, pw)
        except NetError as e:
            self.push_net('failed', (e.code, str(e)))
            return
        except Exception as e:
            self.push_net('failed', (ERR_NET, str(e)))
            return
        self.push_net('connected', mode)

    def on_net_event(self, kind, data):
        self.push_net(kind, data)

    def push_net(self, kind, data=None):
        try:
            self.net_queue.put((kind, data))
        except Exception:
            pass

    def poll_net(self):
        try:
            while True:
                kind, data = self.net_queue.get_nowait()
                try:
                    self.handle_net_event(kind, data)
                except Exception:
                    pass
        except queue.Empty:
            pass
        except Exception:
            pass
        try:
            self.win3.after(80, self.poll_net)
        except Exception:
            pass

    def handle_net_event(self, kind, data):
        global play_state, multiplayer_mode, current_room_count

        if kind == 'connected':
            if current_room_count >= 2:
                self._status("对手已加入，游戏开始！")
            else:
                self._status("等待对手加入...")

        elif kind == 'room_info':
            current_room_count = data
            if current_room_count >= 2:
                if play_state != 1:
                    play_state = 1
                    params.play_state = 1
                    self._status("对手已加入，游戏开始！")
                else:
                    self._status("对手已加入，游戏开始！")
            else:
                play_state = 0
                params.play_state = 0
                self._status("等待对手加入...")

        elif kind == 'failed':
            code, raw = data
            self._net_failed(code, raw)

        elif kind == 'move':
            self.apply_remote_move(data)

        elif kind == 'left':
            if self.net is not None:
                self._end_net(eng_chn_li[137][eng_chn])

        elif kind == 'closed':
            if self.net is not None:
                self._end_net(eng_chn_li[143][eng_chn])

    def _net_failed(self, code, raw):
        global play_state, multiplayer_mode, current_room_count
        play_state = 0
        params.play_state = 0
        current_room_count = 0
        self.close_net()
        self._status(eng_chn_li[122][eng_chn])
        multiplayer_mode = 0
        params.multiplayer_mode = 0
        msg = {
                  ERR_AUTH: eng_chn_li[139][eng_chn],
                  ERR_FULL: eng_chn_li[138][eng_chn],
                  ERR_BAD_ROOM: eng_chn_li[133][eng_chn],
              }.get(code) or f'{eng_chn_li[141][eng_chn]}\n{raw}'
        messagebox.showerror(eng_chn_li[112][eng_chn], msg)

    def _end_net(self, text):
        global play_state, multiplayer_mode, current_room_count
        play_state = 0
        params.play_state = 0
        current_room_count = 0
        self.close_net()
        self._status(text)
        multiplayer_mode = 0
        params.multiplayer_mode = 0
        messagebox.showwarning(eng_chn_li[112][eng_chn], text)

    def apply_remote_move(self, n):
        global num, q, play_state
        if play_state != 1:
            return
        if not isinstance(n, int) or not 1 <= n <= 121:
            return
        r, c = (n - 1) // 11, (n - 1) % 11
        if q[r][c] != 0:
            return

        my_color = 1 if multiplayer_mode == 1 else 2
        opponent_color = 2 if my_color == 1 else 1

        q[r][c] = opponent_color
        params.q[r][c] = opponent_color
        self.cb.cn_buttons[n].config(text='●' if opponent_color == 1 else '○', state='normal')

        black_count = sum(row.count(1) for row in q)
        white_count = sum(row.count(2) for row in q)
        num = black_count + white_count
        params.num = num

        self.check_two_win()

    def step_move_two(self, n):
        global num, q, play_state, multiplayer_mode
        if play_state != 1:
            return
        if not 1 <= n <= 121:
            return
        if self.cb.cn_buttons[n]['text'] in ('●', '○'):
            return

        black_count = sum(row.count(1) for row in q)
        white_count = sum(row.count(2) for row in q)

        expected_color = 1 if black_count <= white_count else 2

        my_color = 1 if multiplayer_mode == 1 else 2

        if expected_color != my_color:
            return

        r, c = (n - 1) // 11, (n - 1) % 11
        q[r][c] = my_color
        params.q[r][c] = my_color
        self.cb.cn_buttons[n].config(text='●' if my_color == 1 else '○')

        num = black_count + white_count + 1
        params.num = num

        if multiplayer_mode in (1, 2) and self.net is not None:
            self.net.send_move(n)

        self.check_two_win()

    def check_two_win(self):
        global play_state, current_room_count
        w = check(q)
        if not w:
            return
        play_state = 0
        params.play_state = 0
        current_room_count = 0

        online = multiplayer_mode in (1, 2)
        my_color = 1 if multiplayer_mode == 1 else 2
        if online:
            msg = eng_chn_li[106][eng_chn] if w == my_color else eng_chn_li[110][eng_chn]
        else:
            msg = eng_chn_li[108][eng_chn] if w == 1 else eng_chn_li[109][eng_chn]
        messagebox.showinfo(eng_chn_li[111][eng_chn], msg)

        try:
            apply_game_result(w == my_color, is_online=online)
        except Exception:
            pass

        self.close_net()
        self._status(eng_chn_li[122][eng_chn])

    def change_nums(self, n):
        global play_num, up_state, multiplayer_mode, current_room_count
        if n != 3:
            self.close_net()
            multiplayer_mode = 0
            params.multiplayer_mode = 0
            current_room_count = 0
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
                self.mp.d_labels[23].config(command=self.history_page_make)
        elif n == 5:
            if up_state != 2:
                if up_state == 0:
                    for i in range(1, 124): self.cb.cn_buttons[i].destroy()
                if up_state == 1:
                    for i in range(26): self.mp.d_labels[i].destroy()
                up_state = 2
            self.ab = About(self.win3)

    def history_page_make(self):
        History()


if __name__ == '__main__':
    MainUIWindow()