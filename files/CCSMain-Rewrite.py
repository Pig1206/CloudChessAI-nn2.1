import tkinter as tk
import json
import datetime as dt
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import os, datetime
import random as rd
import files_old.CCS_CoreNetWork as C3
from files_old.CCS_CEI import eng_chn_li
from tkinter import ttk
import websocket
import threading
from tkinter import font
from PIL import ImageFont
from files_old.hash_PSD import hash
from tkinter import simpledialog
from tkinter import filedialog
import copy

#字体初始化
prf, prz, prh = ImageFont.truetype('fonts\\simfang.TTF'), ImageFont.truetype('fonts\\simzhong.ttf'), ImageFont.truetype('fonts\\simhei.ttf')
pf, pz, ph = prf.getname()[0], prz.getname()[0], prh.getname()[0]

jd_st=0
def start_win():
    def start_main_program():
        start_window.destroy()  # 关闭启动界面
        FQAI_all_code()  # 启动主程序
    def cheng_jd():
        global jd_st
        jd_st+=2
        version_label.config(text='-  '+str(jd_st) +' %  -')
        if jd_st>=100:
            start_main_program()
        else:
            start_window.after(30, cheng_jd)
    # 创建启动界面
    start_window = tk.Tk()
    start_window.geometry('250x100+500+300')
    start_window.configure(bg='light cyan')
    start_window.resizable(False, False)
    start_window.overrideredirect(True)
    img = Image.open('images\\云棋AI-PNG.png')
    img2 = ImageTk.PhotoImage(img)
    bg1 = tk.Label(start_window, image=img2, bg='light cyan')
    bg1.place(x=0, y=-1)
    # 欢迎信息
    welcome_label = tk.Label(start_window, text='云棋AI(Nv2.1)', bg='light cyan', font=font.Font(family=pf,size=15))
    welcome_label.place(x=90, y=20)

    # 版本信息
    version_label = tk.Label(start_window, text='-  0 %  -', bg='light cyan',font=font.Font(family=pf,size=13))
    version_label.place(x=120, y=55)
    cheng_jd()
    # 运行启动界面
    start_window.mainloop()

#核心算法
def _ws_url(room, pw):
    """拼接联机地址：/room/<房号>?pw=<密码>，密码为空则不带参数"""
    from urllib.parse import quote
    url = f'{WS_URL}/room/{quote(room, safe="")}'
    if pw:
        url += '?pw=' + quote(pw, safe='')
    return url

def _ws_err(e):
    """把 WebSocket 握手错误翻译成人话"""
    s = str(e)
    if '403' in s:
        return '密码错误，请向房主确认'
    if '409' in s:
        return '房间已满（最多两人）'
    if '400' in s:
        return '房间号不合法'
    return s

def ws_send_move(n):
    global ws_conn
    try:
        ws_conn.send(json.dumps({'action': 'move', 'room': room_id, 'n': n}))
    except:
        pass

def ws_receive_loop(win3):
    global num, q, play_state, multiplayer_mode
    while play_state == 1 and play_num == 3 and multiplayer_mode in [1, 2]:
        try:
            raw = ws_conn.recv()
            data = json.loads(raw)
            if data.get('type') == 'move':
                n = data['n']
                ns = n - 1
                if multiplayer_mode == 1:
                    q[ns // 11][n % 11 - 1] = 1
                    win3.after(0, lambda nn=n: cn_buttons[nn].config(text='●'))
                else:
                    q[ns // 11][n % 11 - 1] = 2
                    win3.after(0, lambda nn=n: cn_buttons[nn].config(text='○'))
                num += 1
            elif data.get('type') == 'opponent_left':
                win3.after(0, lambda: messagebox.showwarning(eng_chn_li[112][eng_chn], eng_chn_li[113][eng_chn]))
                play_state = 0
        except:
            break
class CCScore(C3.CCScore):
    def __init__(self, chess, difficulty=400, ai_player=2):
        super().__init__(chess, difficulty)
        self.ai_player = ai_player  # AI的棋子颜色
        self.human_player = 1

def check(board):
    board_size = len(board)
    directions = [(1, 0), (0, 1), (1, 1), (1, -1)]  # 水平、垂直、对角线

    # 遍历整个棋盘
    for y in range(board_size):
        for x in range(board_size):
            if board[y][x] == 0:
                continue

            player = board[y][x]
            # 检查四个方向
            for dx, dy in directions:
                count = 1
                # 正向检查
                for i in range(1, 5):
                    nx, ny = x + dx * i, y + dy * i
                    if 0 <= nx < board_size and 0 <= ny < board_size and board[ny][nx] == player:
                        count += 1
                    else:
                        break
                # 如果找到五连珠，直接返回获胜方
                if count >= 5:
                    return player
    return None

#读取用户数据
f1 = open('files_old\\YQ_DataBase.json', 'r')
ms = json.loads(f1.read())
f1.close()
cj_ku = []
def cj_create():
    global cj_ku
    cj_ku = []
    #简单残局(1-10) 等级1解锁 - 需要2-3步连杀
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,1,1,0,0,0,0,0],[0,0,0,0,2,2,2,0,0,0,0],[0,0,0,1,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '双线压制', 1, 1, (6,3)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,2,2,0,0,0,0,0,0],[0,0,0,1,0,0,0,0,0,0,0],[0,0,0,0,1,0,1,0,0,0,0],[0,0,0,0,0,2,0,0,0,0,0],[0,0,0,0,0,0,2,0,0,0,0],[0,0,0,0,0,0,0,2,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '四连堵截', 1, 2, (5,4)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,1,0,0,0,0,0,0,0],[0,0,1,0,2,2,0,0,0,0,0],[0,0,0,0,2,1,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '斜线突围', 1, 1, (5,3)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,2,0,0,0,0,0],[0,0,0,0,2,1,0,0,0,0,0],[0,0,0,2,0,0,2,0,0,0,0],[0,0,0,0,1,0,0,1,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '双三连杀', 1, 1, (6,5)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,1,0,2,0,0,0,0,0],[0,0,1,0,2,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,2,1,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '暗藏杀机', 1, 1, (8,7)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,2,2,0,0,0,0,0,0],[0,0,0,0,0,2,0,0,0,0,0],[0,0,0,0,1,0,2,0,0,0,0],[0,0,0,1,0,0,0,0,0,0,0],[0,0,1,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '五连伏击', 1, 2, (4,3)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,2,2,2,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,1,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '四面楚歌', 1, 1, (6,4)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,2,1,0,0,0,0,0],[0,0,0,2,1,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,1,0,1,2,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '上下联动', 1, 1, (8,4)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,2,2,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,0,2,1,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '跳三冲四', 1, 1, (5,6)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,1,0,2,0,0,0,0,0],[0,0,0,0,1,2,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,2,1,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '两边夹击', 1, 2, (6,6)])
    #中等残局(11-25) 等级3解锁 - 需要3-4步连杀
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,2,1,0,0,0,0,0],[0,0,0,1,0,2,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,2,1,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '双重陷阱', 3, 1, (5,3)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,2,0,0,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,1,0,0,2,0,0,0,0,0],[0,0,0,1,0,0,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,1,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '长龙锁喉', 3, 1, (8,3)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,1,2,0,0,0,0,0,0],[0,0,0,2,1,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,1,2,0,0,0,0,0],[0,0,0,0,0,1,2,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '多重包围', 3, 1, (5,3)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,0,1,2,0,0,0,0,0],[0,0,0,1,0,1,2,0,0,0,0],[0,0,0,0,0,2,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '一子双杀', 3, 1, (5,3)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,2,0,0,0,0,0],[0,0,0,0,2,1,0,0,0,0,0],[0,0,0,2,0,0,1,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '十字连杀', 3, 1, (7,4)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,2,0,2,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,1,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '跳杀', 3, 1, (7,4)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,1,2,0,1,0,0,0,0],[0,0,0,0,2,1,2,0,0,0,0],[0,0,0,0,1,2,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '三三点杀', 3, 1, (6,3)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,1,2,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0,0,0,0],[0,0,0,0,1,2,0,0,0,0,0],[0,0,0,0,0,2,1,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '阶梯杀', 3, 1, (6,5)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,0,2,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,1,2,1,2,0,0,0,0],[0,0,0,0,1,2,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '破空斩', 3, 1, (4,5)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,2,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,2,1,0,0,0,0,0,0],[0,0,0,0,0,0,1,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '角部绞杀', 3, 1, (6,3)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,2,1,0,0,0,0,0,0],[0,0,2,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,1,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '大斜线', 3, 1, (8,5)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,1,2,0,0,0,0,0],[0,0,0,2,1,0,0,0,0,0,0],[0,0,2,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,1,0,1,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '左右互搏', 3, 1, (6,2)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,1,2,0,0,0,0,0,0],[0,0,1,0,0,0,0,0,0,0,0],[0,0,0,0,0,2,2,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '断点连击', 3, 1, (7,6)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,2,1,2,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,1,2,1,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '底路反攻', 3, 1, (6,5)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,1,2,0,0,0,0,0],[0,0,0,0,2,1,2,0,0,0,0],[0,0,0,0,1,2,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '中路突破', 3, 1, (8,5)])
    #困难残局(26-40) 等级5解锁 - 需要4-5步连杀
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,2,0,2,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,2,1,0,0,0,0,0],[0,0,0,1,0,0,2,0,0,0,0],[0,0,0,0,0,0,1,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '天地劫', 5, 1, (5,4)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,0,1,2,0,0,0,0,0],[0,0,0,1,2,0,0,0,0,0,0],[0,0,1,2,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '悬崖杀', 5, 1, (3,6)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,1,0,0,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,0,0,2,0,0,0,0,0],[0,0,0,1,2,1,2,0,0,0,0],[0,0,0,0,1,2,1,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '缠绕阵', 5, 1, (5,3)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,2,0,0,0,0,0],[0,0,0,0,2,1,0,0,0,0,0],[0,0,0,2,1,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,1,2,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '声东击西', 5, 1, (7,5)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,2,0,0,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,0,0,2,0,0,0,0,0],[0,0,0,1,0,0,2,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,1,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '长蛇阵', 5, 1, (6,5)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,2,0,0,0,0,0],[0,0,0,0,2,1,2,0,0,0,0],[0,0,0,1,0,2,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '花心杀', 5, 1, (6,4)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,2,1,0,0,0,0,0],[0,0,0,2,1,0,0,0,0,0,0],[0,0,2,1,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,1,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '反斜杀', 5, 1, (8,5)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,1,0,2,0,0,0,0,0],[0,0,0,0,1,2,1,0,0,0,0],[0,0,0,0,0,0,2,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '双翅杀', 5, 1, (6,4)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,1,2,2,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '跷跷板', 5, 1, (9,4)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,1,2,0,0,0,0,0],[0,0,0,0,2,1,0,0,0,0,0],[0,0,0,0,1,2,1,0,0,0,0],[0,0,0,0,0,0,2,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '叠杀', 5, 1, (7,7)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,0,1,2,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,2,1,2,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '七巧板', 5, 1, (5,5)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,2,0,1,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,0,0,2,0,0,0,0,0],[0,0,0,0,1,0,2,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '双龙出海', 5, 1, (6,7)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,2,1,2,0,0,0,0,0],[0,0,0,0,2,1,0,0,0,0,0],[0,0,0,0,0,2,1,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '倒钩杀', 5, 1, (6,6)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,2,0,0,0,0,0],[0,0,0,0,2,1,0,0,0,0,0],[0,0,0,0,1,2,0,0,0,0,0],[0,0,0,1,0,0,0,0,0,0,0],[0,0,1,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '鬼手', 5, 1, (5,5)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,2,1,0,0,0,0,0,0],[0,0,0,0,2,1,0,0,0,0,0],[0,0,0,0,0,2,0,0,0,0,0],[0,0,0,0,1,0,2,0,0,0,0],[0,0,0,0,0,0,1,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '连环劫', 5, 1, (7,5)])
    #大师残局(41-50) 等级8解锁 - 需要5-7步连杀
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,2,1,0,0,0,0,0,0],[0,0,0,1,2,1,0,0,0,0,0],[0,0,2,0,1,2,0,0,0,0,0],[0,0,0,0,2,1,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '千层网', 8, 1, (3,5)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,1,2,1,0,0,0,0,0],[0,0,1,2,1,2,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '龙虎斗', 8, 1, (5,6)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,2,0,0,0,0,0],[0,0,0,0,2,1,2,0,0,0,0],[0,0,0,2,1,2,1,0,0,0,0],[0,0,0,1,2,1,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '棋筋', 8, 1, (4,6)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,1,2,1,0,0,0,0,0],[0,0,1,2,1,2,0,0,0,0,0],[0,0,0,1,2,0,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '迷魂阵', 8, 1, (4,6)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,2,1,0,0,0,0,0],[0,0,0,0,1,2,1,0,0,0,0],[0,0,0,0,2,1,2,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '金字塔', 8, 1, (4,7)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,1,2,1,0,0,0,0,0],[0,0,0,2,1,2,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '阴阳杀', 8, 1, (4,5)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,1,2,0,0,0,0,0,0],[0,0,0,2,1,2,0,0,0,0,0],[0,0,0,1,2,1,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,1,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '突刺', 8, 1, (6,4)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,2,1,0,0,0,0,0,0],[0,0,0,1,2,2,0,0,0,0,0],[0,0,1,2,1,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '毒蛇', 8, 1, (5,5)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,0,1,2,0,0,0,0,0],[0,0,0,2,1,2,1,0,0,0,0],[0,0,0,0,2,1,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '双劫杀', 8, 1, (5,5)])
    cj_ku.append([[[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,2,0,0,0,0,0,0],[0,0,0,2,1,2,0,0,0,0,0],[0,0,0,1,2,1,2,0,0,0,0],[0,0,0,0,1,2,1,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0,0,0]], '九天劫', 8, 1, (4,6)])
cj_create()
# 全局变量初始化
bg = 'yellow'    # 背景色
num = 0          # 步数计数器
q = [[0 for _ in range(11)] for _ in range(11)]     # 棋盘状态（16位字符串，0为空，1为玩家，2为AI）
s_n = 4          # 剩余登录尝试次数
play_num = 1     # 游戏模式（1-AI先手，2-AI后手，3-双人）
play_state = 0   # 游戏状态（0-未开始，1-进行中）
num2_state = 0   # 双人模式回合状态
up_state = 0     # 界面状态（0-主界面，1-个人信息，2-关于）
eng_chn = 0      # 语言切换
person = {}      # 当前登录用户信息
model = 'NW4.3-M200'  #模型选择
multiplayer_mode = 0  # 0-线下对战, 1-联机对战(主机), 2-联机对战(客户端)
connection = None  # 网络连接对象
WS_URL = 'wss://ccs.ts37699393.workers.dev'
room_id = ''
ws_conn = None
server='12345'
cj_list = [
    {'name': '初出茅庐', 'desc': '完成第一局对局', 'type': 'game_num', 'goal': 1, 'reward': '云币+5'},
    {'name': '百战老将', 'desc': '累计完成100局对局', 'type': 'game_num', 'goal': 100, 'reward': '云币+20'},
    {'name': '首胜之光', 'desc': '获得第一场胜利', 'type': 'win_num', 'goal': 1, 'reward': '云币+5'},
    {'name': '常胜将军', 'desc': '累计获胜50次', 'type': 'win_num', 'goal': 50, 'reward': '云币+30'},
    {'name': '棋圣降世', 'desc': '累计获胜200次', 'type': 'win_num', 'goal': 200, 'reward': '云币+66'},
    {'name': '破产边缘', 'desc': '累计失败30局', 'type': 'lose_num', 'goal': 30, 'reward': '云币+20'},
    {'name': 'AI克星', 'desc': '在MNX1.0-12难度下战胜AI', 'type': 'beat_hard', 'goal': 1, 'reward': '云币+5'},
    {'name': '社交达人', 'desc': '完成一次联机对战', 'type': 'online_num', 'goal': 1, 'reward': '云币+5'},
    {'name': '残局高手', 'desc': '破解10个残局', 'type': 'cj_win', 'goal': 10, 'reward': '云币+10'},
    {'name': '残局大师', 'desc': '破解30个残局', 'type': 'cj_win', 'goal': 30, 'reward': '云币+25'},
    {'name': '十连胜', 'desc': '连胜10局', 'type': 'lian_win', 'goal': 10, 'reward': '云币+35'},
    {'name': '等级飞升', 'desc': '达到Lv.10', 'type': 'level10', 'goal': 1, 'reward': '云币+30'},
]

d = eng_chn_li[2][eng_chn]    # 密码显示状态
d2 = eng_chn_li[2][eng_chn]   # 密码显示状态

def make_circle_img(img_path, size=(80, 80)):
    try:
        im = Image.open(img_path).convert("RGBA")
        im = im.resize(size, Image.Resampling.LANCZOS)

        # 创建圆形mask
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)

        # 应用mask
        result = Image.new('RGBA', size, (0, 0, 0, 0))
        result.paste(im, (0, 0), mask)
        return result
    except:
        # 如果图片不存在，返回默认头像
        im = Image.new('RGBA', size, (200, 200, 200, 255))
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, size[0], size[1]), fill=255)
        result = Image.new('RGBA', size, (0, 0, 0, 0))
        result.paste(im, (0, 0), mask)
        return result
def check_cj(person_data):
    got_new = False
    old_cj = person_data.get('cj_done', [])
    new_cj_list = old_cj.copy()
    total_add = 0
    new_names = []
    for cj in cj_list:
        if cj['name'] in old_cj:
            continue
        shuxing = cj['type']
        goal = cj['goal']
        a = False

        if shuxing == 'game_num':
            val = person_data.get('game_num', 0)
            if val >= goal: a = True
        elif shuxing == 'win_num':
            val = person_data.get('win_num', 0)
            if val >= goal: a = True
        elif shuxing == 'lose_num':
            val = person_data.get('lose_num', 0)
            if val >= goal: a = True
        elif shuxing == 'beat_hard':
            val = person_data.get('beat_hard', 0)
            if val >= goal: a = True
        elif shuxing == 'online_num':
            val = person_data.get('online_num', 0)
            if val >= goal: a = True
        elif shuxing == 'cj_win':
            val = person_data.get('cj_win', 0)
            if val >= goal: a = True
        elif shuxing == 'lian_win':
            val = person_data.get('lian_win_max', 0)
            if val >= goal: a = True
        elif shuxing == 'level10':
            val = person_data.get('level', 1)
            if val >= 10: a = True

        if a:
            new_cj_list.append(cj['name'])
            got_new = True
            new_names.append(cj['name'])
            qifen = int(cj['reward'].replace('云币+', ''))
            total_add += qifen

    if got_new:
        person_data['cj_done'] = new_cj_list
        person_data['YH_number'] = person_data.get('YH_number', 0) + total_add
        person_data['level'] = person_data['YH_number'] // 100 + 1
        msg = '恭喜达成成就：\n'
        for nm in new_names:
            for cj in cj_list:
                if cj['name'] == nm:
                    msg += f'{cj["name"]}  {cj["desc"]}  {cj["reward"]}\n'
        messagebox.showinfo(eng_chn_li[14][eng_chn], msg)
    return got_new

def apply_game_result(is_win, is_online=False, is_hard=False, is_cj=False):
    global person, ms
    f1 = open('files_old\\YQ_DataBase.json', 'r')
    rt = json.loads(f1.read())
    f1.close()
    pdata = rt[person['name']]
    if 'game_num' not in pdata: pdata['game_num'] = 0
    if 'lose_num' not in pdata: pdata['lose_num'] = 0
    if 'beat_hard' not in pdata: pdata['beat_hard'] = 0
    if 'online_num' not in pdata: pdata['online_num'] = 0
    if 'cj_win' not in pdata: pdata['cj_win'] = 0
    if 'cj_done' not in pdata: pdata['cj_done'] = []
    if 'lian_win_max' not in pdata: pdata['lian_win_max'] = 0
    if 'lian_win_now' not in pdata: pdata['lian_win_now'] = 0

    if is_cj:
        pdata['cj_win'] = pdata.get('cj_win', 0) + 1
        pdata['win_num'] = pdata.get('win_num', 0) + 1
        pdata['lian_win_now'] = pdata.get('lian_win_now', 0) + 1
        if pdata['lian_win_now'] > pdata.get('lian_win_max', 0):
            pdata['lian_win_max'] = pdata['lian_win_now']
    else:
        pdata['game_num'] = pdata.get('game_num', 0) + 1
        if is_online:
            pdata['online_num'] = pdata.get('online_num', 0) + 1
        if is_win:
            pdata['win_num'] = pdata.get('win_num', 0) + 1
            pdata['lian_win_now'] = pdata.get('lian_win_now', 0) + 1
            if pdata['lian_win_now'] > pdata.get('lian_win_max', 0):
                pdata['lian_win_max'] = pdata['lian_win_now']
            if is_hard:
                pdata['beat_hard'] = pdata.get('beat_hard', 0) + 1
        else:
            pdata['lose_num'] = pdata.get('lose_num', 0) + 1
            pdata['lian_win_now'] = 0
    pdata['level'] = int(pdata.get('YH_number', 0)) // 100 + 1
    check_cj(pdata)
    with open('files\\YQ_DataBase.json', 'w') as f2:
        f2.writelines(json.dumps(rt))
    person.clear()
    person.update(pdata)

def FQAI_all_code():
    win = tk.Tk()
    win.geometry('320x370+120+120')
    win.title(eng_chn_li[0][eng_chn])
    win.config(background='light cyan')
    win.resizable(False,False)
    win.iconbitmap('images\\云棋AI.ico')
    img = Image.open(eng_chn_li[1][eng_chn])
    img2 = ImageTk.PhotoImage(img)
    bg1 = tk.Label(win, image=img2, bg='light cyan')
    bg1.place(x=-1, y=-3)

    def change():
        global d
        if d == eng_chn_li[2][eng_chn]:
            d = eng_chn_li[3][eng_chn]
            de.config(text=d)
            mm.config(show='')
        elif d == eng_chn_li[3][eng_chn]:
            d = eng_chn_li[2][eng_chn]
            de.config(text=d)
            mm.config(show='•')

    def eng_chn_chg():
        global eng_chn, d, d2
        if eng_chn == 0:
            eng_chn = 1
        elif eng_chn == 1:
            eng_chn = 0
        d = eng_chn_li[2][eng_chn]    # 密码显示状态
        d2 = eng_chn_li[2][eng_chn]   # 密码显示状态
        win.destroy()
        FQAI_all_code()

    def cstart():
        global s_n, ms, person
        if name2.get() != '' and mm.get() != '':
            if name2.get() in ms.keys():
                sal, has = ms[name2.get()]['password'].split(':')
                if hash(mm.get(), sal)[1] == has:
                    person = ms[name2.get()]
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
                    def run_CCS():
                        def change_C(n):
                            global num, play_num, play_state, q, num2_state, person, connection, multiplayer_mode

                            if play_state == 1:
                                if cn_buttons[n]['text'] != '○' and cn_buttons[n]['text'] != '●':
                                    if play_num == 1 or play_num==2:
                                        ns = n - 1
                                        row = ns // 11
                                        col = ns % 11
                                        q[row][col] = 1  # 玩家落子
                                        cn_buttons[n].config(text='●')
                                        if check(q) == 1:
                                            messagebox.showinfo(eng_chn_li[111][eng_chn], eng_chn_li[106][eng_chn])
                                            play_state = 0
                                            num2_state = 0
                                            f1 = open('files_old\\YQ_DataBase.json', 'r')
                                            rt = json.loads(f1.read())
                                            f1.close()
                                            if model == 'NW4.3-M100':
                                                rt[person['name']]['YH_number'] = rt[person['name']].get('YH_number', 0) + 2
                                            elif model == 'NW4.3-M200':
                                                rt[person['name']]['YH_number'] = rt[person['name']].get('YH_number', 0) + 5
                                            elif model == 'NW4.3-M400':
                                                rt[person['name']]['YH_number'] = rt[person['name']].get('YH_number', 0) + 7
                                            elif model == 'NW4.3-M800':
                                                rt[person['name']]['YH_number'] = rt[person['name']].get('YH_number', 0) + 10
                                            rt[person['name']]['level'] = int(rt[person['name']]['YH_number'])//100+1
                                            with open('files_old\\YQ_DataBase.json', 'w') as f2:
                                                f2.writelines(json.dumps(rt))
                                            person['YH_number'] = rt[person['name']]['YH_number']
                                            person['level'] = rt[person['name']]['level']
                                            apply_game_result(True, is_online=False, is_hard=(model == 'NW4.3-M800'))
                                            with open('files_old\\history.json', 'r') as f3:
                                                rrs = json.loads(f3.read())
                                            rrs[person['name']].update({str(q):['me',str(datetime.datetime.now())]})
                                            with open('files_old\\history.json', 'w') as f4:
                                                f4.write(json.dumps(rrs))

                                        if play_state == 1:
                                            for i in range(1, 122):
                                                cn_buttons[i].config(state='disabled')

                                            def ai_move():
                                                global q, play_state
                                                if model == 'NW4.3-M400':
                                                    loc = CCScore(q, difficulty=400).find_best_move()
                                                elif model == 'NW4.3-M100':
                                                    loc = CCScore(q, difficulty=100).find_best_move()
                                                elif model == 'NW4.3-M800':
                                                    loc = CCScore(q, difficulty=800).find_best_move()
                                                elif model == 'NW4.3-M200':
                                                    loc = CCScore(q, difficulty=200).find_best_move()

                                                q[loc[1]][loc[0]] = 2

                                                def update_ui():
                                                    cn_buttons[loc[1] * 11 + loc[0] + 1].config(text='○')

                                                    if check(q) == 2:
                                                        messagebox.showinfo(eng_chn_li[111][eng_chn],
                                                                            eng_chn_li[107][eng_chn])
                                                        apply_game_result(False)
                                                        with open('files_old\\history.json', 'r') as f3:
                                                            rrs = json.loads(f3.read())
                                                        rrs[person['name']].update(
                                                            {str(q): ['AI', str(datetime.datetime.now())]})
                                                        with open('files_old\\history.json', 'w') as f4:
                                                            f4.write(json.dumps(rrs))

                                                    for i in range(1, 122):
                                                        cn_buttons[i].config(state='normal')

                                                win3.after(0, update_ui)

                                            threading.Thread(target=ai_move, daemon=True).start()
                                            #双人对战
                                    if play_num == 3:
                                        if multiplayer_mode == 0:  # 线下对战
                                            if num % 2 == 0:
                                                ns = n - 1
                                                q[ns // 11][n % 11-1] = 2
                                                cn_buttons[n].config(text='○')
                                                if check(q) == 2:
                                                    messagebox.showinfo(eng_chn_li[111][eng_chn], eng_chn_li[108][eng_chn])
                                                    play_state = 0
                                                    with open('files_old\\history.json', 'r') as f3:
                                                        rrs = json.loads(f3.read())
                                                    rrs[person['name']].update({str(q):['player1',str(datetime.datetime.now())]})
                                                    with open('files_old\\history.json', 'w') as f4:
                                                        f4.write(json.dumps(rrs))
                                            else:
                                                ns = n - 1
                                                q[ns // 11][n % 11-1] = 1
                                                cn_buttons[n].config(text='●')
                                                if check(q) == 1:
                                                    messagebox.showinfo(eng_chn_li[111][eng_chn], eng_chn_li[109][eng_chn])
                                                    play_state = 0
                                                    with open('files_old\\history.json', 'r') as f3:
                                                        rrs = json.loads(f3.read())
                                                    rrs[person['name']].update({str(q):['player2',str(datetime.datetime.now())]})
                                                    with open('files_old\\history.json', 'w') as f4:
                                                        f4.write(json.dumps(rrs))
                                            num += 1

                                        elif multiplayer_mode == 1:  # 联机对战(主机)
                                            if num % 2 == 0:  # 主机回合
                                                ns = n - 1
                                                q[ns // 11][n % 11-1] = 2
                                                cn_buttons[n].config(text='○')
                                                if check(q) == 2:
                                                    messagebox.showinfo(eng_chn_li[111][eng_chn], eng_chn_li[106][eng_chn])
                                                    play_state = 0
                                                    f1 = open('files_old\\YQ_DataBase.json', 'r')
                                                    rt = json.loads(f1.read())
                                                    f1.close()
                                                    rt[person['name']]['YH_number'] = rt[person['name']].get('YH_number', 0) + 10
                                                    rt[person['name']]['level'] = int(rt[person['name']]['YH_number'])//100+1
                                                    with open('files_old\\YQ_DataBase.json', 'w') as f2:
                                                        f2.writelines(json.dumps(rt))
                                                    person['YH_number'] = rt[person['name']]['YH_number']
                                                    person['level'] = rt[person['name']]['level']
                                                    apply_game_result(True, is_online=True)
                                                    with open('files_old\\history.json', 'r') as f3:
                                                        rrs = json.loads(f3.read())
                                                    rrs[person['name']].update({str(q):['me',str(datetime.datetime.now())]})
                                                    with open('files_old\\history.json', 'w') as f4:
                                                        f4.write(json.dumps(rrs))
                                                try:
                                                    ws_send_move(n)
                                                except:
                                                    messagebox.showerror(eng_chn_li[112][eng_chn], eng_chn_li[113][eng_chn])
                                                    play_state = 0
                                            num += 1

                                        elif multiplayer_mode == 2:  # 联机对战(客户端)
                                            if num % 2 == 1:  # 客户端回合
                                                ns = n - 1
                                                q[ns // 11][n % 11-1] = 1
                                                cn_buttons[n].config(text='●')
                                                if check(q) == 1:
                                                    messagebox.showinfo(eng_chn_li[111][eng_chn], eng_chn_li[106][eng_chn])
                                                    play_state = 0
                                                    f1 = open('files_old\\YQ_DataBase.json', 'r')
                                                    rt = json.loads(f1.read())
                                                    f1.close()
                                                    rt[person['name']]['YH_number'] = rt[person['name']].get('YH_number', 0) + 10
                                                    rt[person['name']]['level'] = int(rt[person['name']]['YH_number'])//100+1
                                                    with open('files_old\\YQ_DataBase.json', 'w') as f2:
                                                        f2.writelines(json.dumps(rt))
                                                    person['YH_number'] = rt[person['name']]['YH_number']
                                                    person['level'] = rt[person['name']]['level']
                                                    apply_game_result(True, is_online=True)
                                                    with open('files_old\\history.json', 'r') as f3:
                                                        rrs = json.loads(f3.read())
                                                    rrs[person['name']].update({str(q):['me',str(datetime.datetime.now())]})
                                                    with open('files_old\\history.json', 'w') as f4:
                                                        f4.write(json.dumps(rrs))
                                                try:
                                                    ws_send_move(n)
                                                except:
                                                    messagebox.showerror(eng_chn_li[112][eng_chn], eng_chn_li[113][eng_chn])
                                                    play_state = 0
                                            num += 1

                        win3 = tk.Tk()
                        win3.geometry('360x550+100+100')
                        win3.title(eng_chn_li[0][eng_chn])
                        win3.configure(bg='light cyan')
                        win3.resizable(False,False)
                        win3.iconbitmap('images\\云棋AI.ico')

                        img = Image.open('images\\云棋AI-BG1.png')
                        img2 = ImageTk.PhotoImage(img)
                        bg1 = tk.Label(win3, image=img2)
                        bg1.place(x=-1, y=-3)
                        cn_buttons = {}
                        de_buttons = {}
                        d_labels = {}
                        abo_labels = {}

                        def change_nums(n):
                            global play_num, up_state
                            play_num = n
                            for i in range(1,6):
                                if i != n:
                                    de_buttons[i].config(activebackground='deepskyblue',bg='deepskyblue')
                            de_buttons[n].config(activebackground='whitesmoke',bg='whitesmoke')
                            if n <= 3:
                                if up_state != 0:
                                    if up_state == 2:
                                        for i in range(15):
                                            abo_labels[i].destroy()
                                    if up_state == 1:
                                        for i in range(26):  #Θ◎
                                            d_labels[i].destroy()
                                    up_state = 0
                                    rc_y = 150
                                    for j in range(1, 12):
                                        for i in range(1, 12):
                                            cn_buttons[(j-1)*11+i] = tk.Button(win3,width=2,height=1,activebackground='yellow', command=lambda arg=(j-1)*11+i:change_C(arg),font=font.Font(family=ph,size=13),bg='yellow')
                                            cn_buttons[(j-1)*11+i].place(x=(i-1)*30+20,y=rc_y)
                                        rc_y+=30
                                    cn_buttons[122] = tk.Label(win3,text=eng_chn_li[23][eng_chn],font=font.Font(family=pz,size=13),bg='light cyan')
                                    cn_buttons[122].place(x=60,y=125)#Θ◎
                                    cn_buttons[123] = tk.Button(win3, command=start, width=10,height=1, text=eng_chn_li[23][eng_chn], font=font.Font(family=pz,size=15),activebackground='yellow',bg='yellow')
                                    cn_buttons[123].place(x=110, y=488)
                                if n == 1:
                                    cn_buttons[122].config(text=eng_chn_li[24][eng_chn])
                                if n == 2:
                                    cn_buttons[122].config(text=eng_chn_li[25][eng_chn])
                                if n == 3:
                                    cn_buttons[122].config(text=eng_chn_li[26][eng_chn])
                            elif n == 4:
                                if up_state != 1:
                                    def account_mg():
                                        acc_win = tk.Toplevel(win3)
                                        acc_win.geometry('300x200+250+200')
                                        acc_win.title(eng_chn_li[28][eng_chn])
                                        acc_win.configure(bg='light cyan')
                                        acc_win.resizable(False, False)

                                        tk.Label(acc_win, text=eng_chn_li[28][eng_chn], bg='light cyan', font=font.Font(family=pf, size=18)).place(x=90, y=20)

                                        def open_change():
                                            acc_win.destroy()
                                            change_info()

                                        def open_des():
                                            acc_win.destroy()
                                            change_des()

                                        tk.Button(acc_win, text=eng_chn_li[29][eng_chn], command=open_change, width=15,
                                                  font=font.Font(family=pf, size=14), bg='whitesmoke').place(x=65, y=75)
                                        tk.Button(acc_win, text=eng_chn_li[30][eng_chn], command=open_des, width=15,
                                                  font=font.Font(family=pf, size=14), bg='whitesmoke').place(x=65, y=125)

                                        acc_win.mainloop()

                                    def change_des():
                                        global person, up_state, ms
                                        ask_yn = messagebox.askyesno(eng_chn_li[30][eng_chn], eng_chn_li[31][eng_chn]+person['name']+eng_chn_li[32][eng_chn]+person['ID']+eng_chn_li[33][eng_chn])
                                        if ask_yn:
                                            f1 = open('files_old\\YQ_DataBase.json', 'r')
                                            cst = json.loads(f1.read())
                                            f1.close()
                                            f2 = open('files_old\\YQ_DataBase.json', 'w')
                                            del cst[person['name']]
                                            f2.write(json.dumps(cst))
                                            f2.close()
                                            with open('files_old\\history.json', 'r') as f3:
                                                rrs = json.loads(f3.read())
                                            del rrs[person['name']]
                                            with open('files_old\\history.json', 'w') as f4:
                                                f4.write(json.dumps(rrs))
                                            messagebox.showinfo(eng_chn_li[30][eng_chn], eng_chn_li[34][eng_chn])
                                            if up_state == 0:
                                                for i in range(1, 124):  #Θ◎
                                                    cn_buttons[i].destroy()
                                            if up_state == 2:
                                                for i in range(15):
                                                    abo_labels[i].destroy()
                                            if up_state == 1:
                                                for i in range(26):  #Θ◎
                                                    d_labels[i].destroy()
                                            up_state=0
                                            person={}
                                            win3.destroy()
                                            f1 = open('files_old\\YQ_DataBase.json', 'r')
                                            ms = json.loads(f1.read())
                                            f1.close()
                                            FQAI_all_code()
                                    def change_info():
                                        global person, ms
                                        change_win = tk.Toplevel(win3)
                                        change_win.geometry('400x400+200+150')
                                        change_win.title(eng_chn_li[35][eng_chn])
                                        change_win.configure(bg='light cyan')
                                        change_win.resizable(False, False)

                                        # 临时存储修改的变量
                                        tmp_photo = person.get('photo', '')
                                        tmp_name = person['name']
                                        tmp_pw = ''

                                        # 显示当前头像
                                        photo_path = tmp_photo if tmp_photo else 'images\\Sphotograph.png'
                                        cir_img = make_circle_img(photo_path, (100, 100))
                                        photo_img = ImageTk.PhotoImage(cir_img)
                                        photo_label = tk.Label(change_win, image=photo_img, bg='light cyan')
                                        photo_label.image = photo_img
                                        photo_label.place(x=150, y=20)

                                        def pick_photo():
                                            nonlocal tmp_photo, photo_img, photo_label
                                            file_path = filedialog.askopenfilename(
                                                title=eng_chn_li[35][eng_chn],
                                                filetypes=[('图片文件', '*.png *.jpg *.jpeg *.gif *.bmp')]
                                            )
                                            if file_path:
                                                tmp_photo = file_path
                                                cir_img = make_circle_img(file_path, (100, 100))
                                                photo_img = ImageTk.PhotoImage(cir_img)
                                                photo_label.config(image=photo_img)
                                                photo_label.image = photo_img

                                        tk.Button(change_win, text=eng_chn_li[35][eng_chn], command=pick_photo,
                                                  font=font.Font(family=pf, size=12), bg='whitesmoke', width=10).place(x=150, y=135)

                                        # 名称修改
                                        tk.Label(change_win, text=eng_chn_li[36][eng_chn], bg='light cyan', font=font.Font(family=pf, size=14)).place(x=50, y=190)
                                        name_entry = tk.Entry(change_win, font=font.Font(family=pf, size=14), width=18)
                                        name_entry.insert(0, tmp_name)
                                        name_entry.place(x=150, y=190)

                                        # 密码修改
                                        tk.Label(change_win, text=eng_chn_li[37][eng_chn], bg='light cyan', font=font.Font(family=pf, size=14)).place(x=50, y=230)
                                        pw_entry = tk.Entry(change_win, font=font.Font(family=pf, size=14), width=18, show='•')
                                        pw_entry.place(x=150, y=230)

                                        tk.Label(change_win, text=eng_chn_li[38][eng_chn], bg='light cyan', font=font.Font(family=pf, size=14)).place(x=50, y=270)
                                        pw_entry2 = tk.Entry(change_win, font=font.Font(family=pf, size=14), width=18, show='•')
                                        pw_entry2.place(x=150, y=270)
                                        about_me = tk.Label(change_win, text='◎'+eng_chn_li[0][eng_chn],bg='light cyan',fg='grey', font=font.Font(family=pf,size=9))
                                        about_me.place(x=5, y=360)

                                        def qr_change():
                                            global person, ms
                                            new_name = name_entry.get().strip()
                                            new_pw = pw_entry.get()
                                            new_pw2 = pw_entry2.get()

                                            if not new_name:
                                                messagebox.showwarning(eng_chn_li[39][eng_chn], eng_chn_li[40][eng_chn])
                                                return

                                            # 检查名称是否重复
                                            if new_name != person['name'] and new_name in ms:
                                                messagebox.showwarning(eng_chn_li[39][eng_chn], eng_chn_li[41][eng_chn])
                                                return

                                            # 如果修改了密码
                                            if new_pw:
                                                if new_pw != new_pw2:
                                                    messagebox.showwarning(eng_chn_li[39][eng_chn], eng_chn_li[42][eng_chn])
                                                    return
                                                if new_pw.isnumeric() or new_pw.isalpha() or len(new_pw) < 5 or not new_pw.isalnum():
                                                    messagebox.showwarning(eng_chn_li[39][eng_chn], eng_chn_li[43][eng_chn])
                                                    return

                                            # 保存修改
                                            f1 = open('files_old\\YQ_DataBase.json', 'r')
                                            all_data = json.loads(f1.read())
                                            f1.close()

                                            old_name = person['name']

                                            # 如果名字改了，需要处理key的变化
                                            if old_name != new_name:
                                                all_data[new_name] = all_data.pop(old_name)
                                                # 更新历史记录
                                                with open('files_old\\history.json', 'r') as f3:
                                                    hist_data = json.loads(f3.read())
                                                if old_name in hist_data:
                                                    hist_data[new_name] = hist_data.pop(old_name)
                                                with open('files_old\\history.json', 'w') as f4:
                                                    f4.write(json.dumps(hist_data))

                                            # 更新头像
                                            all_data[new_name]['photo'] = tmp_photo
                                            # 更新名称
                                            all_data[new_name]['name'] = new_name
                                            # 更新密码
                                            if new_pw:
                                                sal, pasw = hash(new_pw)
                                                all_data[new_name]['password'] = f'{sal}:{pasw}'
                                                all_data[new_name]['password_length'] = len(new_pw)

                                            with open('files_old\\YQ_DataBase.json', 'w') as f2:
                                                f2.write(json.dumps(all_data))

                                            # 更新当前用户信息
                                            ms = all_data
                                            person = all_data[new_name]

                                            messagebox.showinfo(eng_chn_li[14][eng_chn], eng_chn_li[46][eng_chn])
                                            change_win.destroy()
                                            global up_state
                                            if up_state == 0:
                                                for i in range(1,124):
                                                    cn_buttons[i].destroy()
                                            if up_state == 2:
                                                for i in range(15):
                                                    abo_labels[i].destroy()
                                            if up_state == 1:
                                                for i in range(26):
                                                    d_labels[i].destroy()
                                            up_state=0
                                            win3.destroy()
                                            run_CCS()

                                        tk.Button(change_win, text=eng_chn_li[44][eng_chn], command=qr_change,
                                                  font=font.Font(family=pf, size=14), bg='whitesmoke', width=10).place(x=60, y=310)
                                        tk.Button(change_win, text=eng_chn_li[45][eng_chn], command=change_win.destroy,
                                                  font=font.Font(family=pf, size=14), bg='whitesmoke', width=10).place(x=230, y=310)

                                        change_win.mainloop()

                                    def history_info():
                                        global person, eng_chn
                                        hist_win = tk.Toplevel()
                                        hist_win.geometry('600x530+250+150')
                                        hist_win.title(eng_chn_li[47][eng_chn])
                                        hist_win.configure(bg='light cyan')
                                        hist_win.resizable(False, False)

                                        tk.Label(hist_win, text=eng_chn_li[48][eng_chn], bg='light cyan', font=font.Font(family=pf, size=12)).place(x=20, y=20)
                                        date_entry = tk.Entry(hist_win, width=15, font=font.Font(family=pf, size=12))
                                        date_entry.place(x=100, y=20)

                                        tk.Label(hist_win, text=eng_chn_li[49][eng_chn], bg='light cyan', font=font.Font(family=pf, size=12)).place(x=250, y=20)
                                        type_combo = ttk.Combobox(hist_win, width=15, values=[eng_chn_li[49][eng_chn], 'AI', 'me', 'player1', 'player2', 'other'])
                                        type_combo.place(x=330, y=20)
                                        type_combo.current(0)

                                        def query():
                                            update_tree()

                                        tk.Button(hist_win, text=eng_chn_li[50][eng_chn], command=query, width=8, font=font.Font(family=pf, size=12),bg='whitesmoke').place(x=480, y=17)

                                        columns = (eng_chn_li[51][eng_chn], eng_chn_li[52][eng_chn], eng_chn_li[53][eng_chn])
                                        tree = ttk.Treeview(hist_win, columns=columns, show='headings', height=18)
                                        tree.heading(eng_chn_li[51][eng_chn], text=eng_chn_li[51][eng_chn])
                                        tree.heading(eng_chn_li[52][eng_chn], text=eng_chn_li[52][eng_chn])
                                        tree.heading(eng_chn_li[53][eng_chn], text=eng_chn_li[53][eng_chn])
                                        tree.column(eng_chn_li[51][eng_chn], width=150)
                                        tree.column(eng_chn_li[52][eng_chn], width=260)
                                        tree.column(eng_chn_li[53][eng_chn], width=140)
                                        tree.place(x=20, y=70)

                                        scrollbar = ttk.Scrollbar(hist_win, orient='vertical', command=tree.yview)
                                        scrollbar.place(x=573, y=70, height=380)
                                        tree.configure(yscrollcommand=scrollbar.set)

                                        def load_history():
                                            try:
                                                with open('files\\history.json', 'r') as f:
                                                    data = json.load(f)
                                                    return data.get(person['name'], {})
                                            except:
                                                return {}

                                        def save_history(history_data):
                                            try:
                                                with open('files\\history.json', 'r') as f:
                                                    all_data = json.load(f)
                                            except:
                                                all_data = {}

                                            all_data[person['name']] = history_data
                                            with open('files\\history.json', 'w') as f:
                                                f.write(json.dumps(all_data))

                                        def update_tree():
                                            for item in tree.get_children():
                                                tree.delete(item)

                                            history = load_history()
                                            date_filter = date_entry.get()
                                            type_filter = type_combo.get()

                                            for board_str, info in history.items():
                                                play_type = info[0]
                                                play_time = info[1]

                                                if date_filter and date_filter not in play_time[:10]:
                                                    continue
                                                if type_filter != eng_chn_li[49][eng_chn] and type_filter != play_type:
                                                    continue

                                                board_preview = board_str[:50] + '...' if len(board_str) > 50 else board_str
                                                tree.insert('', 'end', values=(play_time[:19], board_preview, play_type), tags=(board_str,))

                                        def delete_selected():
                                            selected = tree.selection()
                                            if not selected:
                                                messagebox.showwarning(eng_chn_li[39][eng_chn], eng_chn_li[56][eng_chn])
                                                return

                                            if messagebox.askyesno(eng_chn_li[54][eng_chn], eng_chn_li[57][eng_chn]):
                                                history = load_history()
                                                for item in selected:
                                                    board_str = tree.item(item, 'tags')[0]
                                                    if board_str in history:
                                                        del history[board_str]
                                                save_history(history)
                                                update_tree()
                                                messagebox.showinfo(eng_chn_li[14][eng_chn], eng_chn_li[58][eng_chn])

                                        def delete_all():
                                            if messagebox.askyesno(eng_chn_li[55][eng_chn], eng_chn_li[59][eng_chn]):
                                                save_history({})
                                                update_tree()
                                                messagebox.showinfo(eng_chn_li[14][eng_chn], eng_chn_li[60][eng_chn])

                                        tk.Button(hist_win, text=eng_chn_li[54][eng_chn], command=delete_selected, width=8, font=font.Font(family=pf, size=12),bg='whitesmoke').place(x=20, y=460)
                                        tk.Button(hist_win, text=eng_chn_li[55][eng_chn], command=delete_all, width=8, font=font.Font(family=pf, size=12),bg='whitesmoke').place(x=120, y=460)

                                        about_me= tk.Label(hist_win, text='◎'+eng_chn_li[0][eng_chn],bg='light cyan',fg='gray', font=font.Font(family=pf,size=10))
                                        about_me.place(x=10, y=500)
                                        def show_board(event):
                                            item = tree.selection()[0]
                                            board_str = tree.item(item, 'tags')[0]

                                            try:
                                                board = eval(board_str)
                                            except:
                                                return

                                            board_win = tk.Toplevel(hist_win)
                                            board_win.geometry('400x430+300+200')
                                            board_win.title(eng_chn_li[61][eng_chn])
                                            board_win.configure(bg='yellow')
                                            board_win.resizable(False, False)

                                            for i in range(11):
                                                for j in range(11):
                                                    x, y = j*30+30, i*30+50
                                                    if board[i][j] == 1:
                                                        tk.Label(board_win, text='●', font=font.Font(family=ph, size=15), bg='yellow').place(x=x, y=y)
                                                    elif board[i][j] == 2:
                                                        tk.Label(board_win, text='○', font=font.Font(family=ph, size=15), bg='yellow').place(x=x, y=y)
                                                    else:
                                                        tk.Label(board_win, text='·', font=font.Font(family=ph, size=15), bg='yellow').place(x=x, y=y)

                                        tree.bind('<Double-1>', show_board)
                                        update_tree()
                                    def canju_challenge():
                                        global person
                                        cj_win = tk.Toplevel(win3)
                                        cj_win.geometry('500x570+200+100')
                                        cj_win.title(eng_chn_li[65][eng_chn])
                                        cj_win.configure(bg='light cyan')
                                        cj_win.resizable(False, False)

                                        pl_level = person.get('level', 1)

                                        #筛选已解锁的残局
                                        unlocked = []
                                        for idx, cj in enumerate(cj_ku):
                                            if pl_level >= cj[2]:
                                                unlocked.append((idx+1, cj))

                                        tk.Label(cj_win, text=eng_chn_li[65][eng_chn], bg='light cyan', font=font.Font(family=pf, size=20)).place(x=180, y=10)
                                        tk.Label(cj_win, text=f'{eng_chn_li[66][eng_chn]}{pl_level}   {eng_chn_li[67][eng_chn]}{len(unlocked)}{eng_chn_li[68][eng_chn]}',
                                                 bg='light cyan', font=font.Font(family=pf, size=12)).place(x=100, y=50)
                                        tk.Label(cj_win, text=eng_chn_li[69][eng_chn], bg='light cyan', fg='gray',
                                                 font=font.Font(family=pf, size=10)).place(x=170, y=75)

                                        frame = tk.Frame(cj_win, bg='light cyan')
                                        frame.place(x=20, y=100, width=460, height=430)

                                        canvas = tk.Canvas(frame, bg='light cyan', highlightbackground='light cyan')
                                        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
                                        scrollable_frame = tk.Frame(canvas, bg='light cyan')

                                        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
                                        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                                        canvas.configure(yscrollcommand=scrollbar.set)

                                        for idx, cj in unlocked:
                                            frm = tk.Frame(scrollable_frame, bg='whitesmoke', bd=1, relief='solid')
                                            frm.pack(pady=3, padx=5, fill='x')
                                            tk.Label(frm, text=f'{eng_chn_li[70][eng_chn]}{idx}', bg='whitesmoke', font=font.Font(family=pf, size=12)).pack(side='left', padx=5)
                                            tk.Label(frm, text=cj[1], bg='whitesmoke', font=font.Font(family=pf, size=12)).pack(side='left', padx=10)
                                            tk.Label(frm, text=f'{eng_chn_li[71][eng_chn]}{"★"*max(1,(cj[2]+1)//2)}', bg='whitesmoke', font=font.Font(family=pf, size=10)).pack(side='left', padx=5)

                                            def start_cj(arg_cj=cj, arg_idx=idx):
                                                cj_win.destroy()
                                                open_cj_board(arg_cj, arg_idx)

                                            tk.Button(frm, text=eng_chn_li[72][eng_chn], command=lambda c=cj, i=idx: start_cj(c, i),
                                                      bg='deepskyblue', font=font.Font(family=pf, size=11), width=6).pack(side='right', padx=10)

                                        canvas.pack(side="left", fill="both", expand=True)
                                        scrollbar.pack(side="right", fill="y")
                                        about_me = tk.Label(cj_win, text='◎'+eng_chn_li[0][eng_chn],bg='light cyan',fg='grey', font=font.Font(family=pf,size=9))
                                        about_me.place(x=5, y=550)

                                        cj_win.mainloop()

                                    def open_cj_board(cj_data, cj_num):
                                        global person
                                        cj_board_win = tk.Toplevel(win3)
                                        cj_board_win.geometry('380x480+200+100')
                                        cj_board_win.title(f'{eng_chn_li[65][eng_chn]} #{cj_num}')
                                        cj_board_win.configure(bg='light cyan')
                                        cj_board_win.resizable(False, False)

                                        cj_q = copy.deepcopy(cj_data[0])
                                        cj_turn = cj_data[3]  #1或2，表示当前该谁下
                                        cj_answer = cj_data[4]  #正确答案位置(row, col)

                                        tk.Label(cj_board_win, text=cj_data[1], bg='light cyan', font=font.Font(family=pf, size=14)).place(x=80, y=5)
                                        tk.Label(cj_board_win, text=f'{eng_chn_li[73][eng_chn]}{eng_chn_li[74][eng_chn] if cj_turn==1 else eng_chn_li[75][eng_chn]} {eng_chn_li[73][eng_chn]}',
                                                 bg='light cyan', font=font.Font(family=pf, size=12)).place(x=90, y=35)

                                        #绘制棋盘
                                        cj_btns = {}
                                        rc_y = 70
                                        for j in range(11):
                                            for i in range(11):
                                                txt = ''
                                                if cj_q[j][i] == 1:
                                                    txt = '●'
                                                elif cj_q[j][i] == 2:
                                                    txt = '○'
                                                else:
                                                    txt = ''

                                                def cj_click(n, row=j, col=i):
                                                    nonlocal cj_q, cj_turn
                                                    if cj_q[row][col] != 0:
                                                        return
                                                    if cj_turn == 0:
                                                        return

                                                    player_color = cj_turn
                                                    cj_q[row][col] = player_color
                                                    cj_btns[(row, col)].config(text='●' if player_color == 1 else '○')

                                                    if check(cj_q) == player_color:
                                                        cj_turn = 0
                                                        f1 = open('files_old\\YQ_DataBase.json', 'r')
                                                        rt = json.loads(f1.read())
                                                        f1.close()
                                                        rt[person['name']]['YH_number'] = rt[person['name']].get('YH_number', 0) + 6
                                                        rt[person['name']]['level'] = int(rt[person['name']]['YH_number']) // 100 + 1
                                                        with open('files_old\\YQ_DataBase.json', 'w') as f2:
                                                            f2.writelines(json.dumps(rt))
                                                        person['YH_number'] = rt[person['name']]['YH_number']
                                                        person['level'] = rt[person['name']]['level']
                                                        apply_game_result(True, is_cj=True)
                                                        messagebox.showinfo(eng_chn_li[14][eng_chn], eng_chn_li[76][eng_chn])
                                                        cj_board_win.destroy()
                                                        with open('files_old\\history.json', 'r') as f3:
                                                            rrs = json.loads(f3.read())
                                                        rrs[person['name']].update({str(cj_q): ['me', str(datetime.datetime.now())]})
                                                        with open('files_old\\history.json', 'w') as f4:
                                                            f4.write(json.dumps(rrs))
                                                        return

                                                    ai_color = 3 - player_color
                                                    cj_turn = ai_color

                                                    for i in range(11):
                                                        for j in range(11):
                                                            cj_btns[(i, j)].config(state='disabled')

                                                    def cj_ai_move():
                                                        loc = CCScore(cj_q, difficulty=300,
                                                                      ai_player=ai_color).find_best_move()
                                                        cj_q[loc[1]][loc[0]] = ai_color

                                                        def update_cj_ui():
                                                            nonlocal cj_turn
                                                            cj_btns[(loc[1], loc[0])].config(text='●' if ai_color == 1 else '○')

                                                            if check(cj_q) == ai_color:
                                                                cj_turn = 0
                                                                messagebox.showinfo(eng_chn_li[14][eng_chn], eng_chn_li[77][eng_chn])
                                                                cj_board_win.destroy()
                                                                with open('files_old\\history.json', 'r') as f3:
                                                                    rrs = json.loads(f3.read())
                                                                rrs[person['name']].update({str(cj_q): ['AI', str(datetime.datetime.now())]})
                                                                with open('files_old\\history.json', 'w') as f4:
                                                                    f4.write(json.dumps(rrs))
                                                                return

                                                            cj_turn = 3 - ai_color
                                                            for i in range(11):
                                                                for j in range(11):
                                                                    cj_btns[(i, j)].config(state='normal')

                                                        cj_board_win.after(0, update_cj_ui)

                                                    threading.Thread(target=cj_ai_move, daemon=True).start()

                                                btn = tk.Button(cj_board_win, width=2, height=1, bg='yellow',
                                                                text=txt, font=font.Font(family=ph, size=13),
                                                                command=lambda n=None, r=j, c=i: cj_click(n, r, c))
                                                btn.place(x=i*30+20, y=rc_y)
                                                cj_btns[(j, i)] = btn
                                            rc_y += 30

                                        tk.Button(cj_board_win, text=eng_chn_li[78][eng_chn], command=cj_board_win.destroy,
                                                  bg='whitesmoke', font=font.Font(family=pf, size=12), width=8).place(x=280, y=420)

                                        cj_board_win.mainloop()

                                    def show_cj_list():
                                        """显示成就列表"""
                                        cjlist_win = tk.Toplevel(win3)
                                        cjlist_win.geometry('500x500+200+100')
                                        cjlist_win.title(eng_chn_li[62][eng_chn])
                                        cjlist_win.configure(bg='light cyan')
                                        cjlist_win.resizable(False, False)

                                        tk.Label(cjlist_win, text=eng_chn_li[63][eng_chn], bg='light cyan', font=font.Font(family=pf, size=20)).place(x=160, y=10)

                                        done_cj = person.get('cj_done', [])

                                        frame = tk.Frame(cjlist_win, bg='light cyan')
                                        frame.place(x=20, y=50, width=460, height=400)

                                        canvas = tk.Canvas(frame, bg='light cyan', highlightbackground='light cyan')
                                        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=canvas.yview)
                                        scrollable_frame = tk.Frame(canvas, bg='light cyan')

                                        scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
                                        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
                                        canvas.configure(yscrollcommand=scrollbar.set)

                                        for cj in cj_list:
                                            done = cj['name'] in done_cj
                                            bgc = 'light green' if done else 'whitesmoke'
                                            frm = tk.Frame(scrollable_frame, bg=bgc, bd=1, relief='solid')
                                            frm.pack(pady=3, padx=5, fill='x')
                                            tk.Label(frm, text=f"{'✅' if done else '⬜'} {cj['name']}",
                                                     bg=bgc, font=font.Font(family=pf, size=13)).pack(anchor='w', padx=5)
                                            tk.Label(frm, text=f"  {cj['desc']}  |  成就达成奖励 Award  {cj['reward']}",
                                                     bg=bgc, font=font.Font(family=pf, size=10), fg='gray').pack(anchor='w', padx=5)

                                        canvas.pack(side="left", fill="both", expand=True)
                                        scrollbar.pack(side="right", fill="y")
                                        about_me = tk.Label(cjlist_win, text='◎'+eng_chn_li[0][eng_chn],bg='light cyan',fg='grey', font=font.Font(family=pf,size=9))
                                        about_me.place(x=5, y=470)
                                        cjlist_win.mainloop()
                                    if up_state == 0:
                                        for i in range(1, 124):  #Θ◎
                                            cn_buttons[i].destroy()
                                    if up_state == 2:
                                        for i in range(15):
                                            abo_labels[i].destroy()
                                    up_state = 1
                                    str_list = eng_chn_li[27][eng_chn].split()
                                    lir = ['name', 'YH_number', 'ID', 'password', 'level', 'win_num']
                                    for i in range(13, 20):
                                        d_labels[i] = tk.Canvas(win3,width=500,height=1, bd=0, bg='light gray', highlightbackground='light cyan')
                                        d_labels[i].place(x=0,y=150+(i-13)*45)

                                    # 显示圆形头像
                                    photo_path = person.get('photo', '')
                                    if not photo_path:
                                        photo_path = 'images\\Sphotograph.png'
                                    cir_img = make_circle_img(photo_path, (35, 35))
                                    photo_tk = ImageTk.PhotoImage(cir_img)
                                    d_labels[25] = tk.Label(win3, image=photo_tk, bg='light cyan')
                                    d_labels[25].image = photo_tk
                                    d_labels[25].place(x=190, y=110)

                                    for i in range(7):
                                        d_labels[i] = tk.Label(win3,text=str_list[i],font=font.Font(family=pf,size=15),bg='light cyan')
                                        d_labels[i].place(x=20,y=120+i*45)
                                    for i in range(7, 13):
                                        if lir[i-7] == 'password':
                                            pw_show = '*' * person.get('password_length', 8)
                                            d_labels[i] = tk.Label(win3,text=pw_show,font=font.Font(family=pf,size=15),bg='light cyan')
                                        elif lir[i-7] == 'level':
                                            d_labels[i] = tk.Label(win3,text='Lv.'+str(person[lir[i-7]]),font=font.Font(family=pf,size=15),bg='light cyan')
                                        else:
                                            d_labels[i] = tk.Label(win3,text=person[lir[i-7]],font=font.Font(family=pf,size=15),bg='light cyan')
                                        d_labels[i].place(x=195,y=165+(i-7)*45)
                                    d_labels[20] = tk.Button(win3, text=eng_chn_li[28][eng_chn],width=13,font=font.Font(family=pf,size=15),activebackground='whitesmoke',bg='whitesmoke', command=account_mg)
                                    d_labels[20].place(x=30, y=435)
                                    d_labels[21] = tk.Button(win3,command=show_cj_list, text=eng_chn_li[62][eng_chn],width=13, font=font.Font(family=pf,size=15),activebackground='whitesmoke',bg='whitesmoke')
                                    d_labels[21].place(x=190, y=435)
                                    d_labels[22] = tk.Canvas(win3,width=1,height=310, bd=0, bg='light gray', highlightbackground='light cyan')
                                    d_labels[22].place(x=130,y=110)
                                    d_labels[23] = tk.Button(win3, text=eng_chn_li[47][eng_chn],command=history_info,width=13, font=font.Font(family=pf,size=15),activebackground='whitesmoke',bg='whitesmoke')
                                    d_labels[23].place(x=30, y=475)
                                    d_labels[24] = tk.Button(win3, text=eng_chn_li[64][eng_chn],command=canju_challenge,width=13, font=font.Font(family=pf,size=15),activebackground='whitesmoke',bg='whitesmoke')
                                    d_labels[24].place(x=190, y=475)

                            elif n == 5:
                                if up_state != 2:
                                    if up_state == 0:
                                        for i in range(1,124):  #Θ◎
                                            cn_buttons[i].destroy()
                                    if up_state == 1:
                                        for i in range(26):
                                            d_labels[i].destroy()
                                    up_state = 2
                                    al= eng_chn_li[119][eng_chn]
                                    al2 = al.split('\n')
                                    y=120
                                    for i in range(11):
                                        abo_labels[i] = tk.Label(win3, text=al2[i],bg='light cyan', font=font.Font(family=pf,size=15))
                                        abo_labels[i].place(x=10, y=y)
                                        y+=25
                                    def function1(arg):
                                        messagebox.showinfo(eng_chn_li[115][eng_chn], '1.李忠良，陈莉\n2.宫城老师，孙玉燕老师\n3.CSDN社区\n4.JetBrain\n5.deepseek深度求索')
                                    def function2(arg):
                                        messagebox.showinfo(eng_chn_li[116][eng_chn], eng_chn_li[117][eng_chn])
                                    abo_labels[9].bind('<Double-Button-1>', function1)
                                    abo_labels[10].bind('<Double-Button-1>', function2)
                                    def close():
                                        win3.destroy()
                                    def re_start():
                                        global up_state, ms, st
                                        if up_state == 0:
                                            for i in range(1,124):  #Θ◎
                                                cn_buttons[i].destroy()
                                        if up_state == 2:
                                            for i in range(15):
                                                abo_labels[i].destroy()
                                        if up_state == 1:
                                            for i in range(26):  #Θ◎
                                                d_labels[i].destroy()
                                        up_state=0
                                        win3.destroy()
                                        f1 = open('files_old\\YQ_DataBase.json', 'r')
                                        ms = json.loads(f1.read())
                                        f1.close()
                                        FQAI_all_code()
                                    abo_labels[11] = tk.Label(win3, text=eng_chn_li[118][eng_chn],bg='light cyan', font=font.Font(family=pf,size=15), fg='red')
                                    abo_labels[11].place(x=10, y=400)
                                    abo_labels[12] = tk.Button(win3, command=re_start, width=10, text=eng_chn_li[79][eng_chn], font=font.Font(family=pf,size=15),activebackground='whitesmoke',bg='whitesmoke')
                                    abo_labels[12].place(x=50, y=435)
                                    abo_labels[13] = tk.Button(win3, command=close, width=10, text=eng_chn_li[80][eng_chn], font=font.Font(family=pf,size=15),activebackground='whitesmoke',bg='whitesmoke')
                                    abo_labels[13].place(x=200, y=435)
                                    global img, img2
                                    img = Image.open(os.path.abspath('images\\山西广寰图片.png'))
                                    img2 = ImageTk.PhotoImage(img)
                                    abo_labels[14] = tk.Label(win3, image=img2, bg='light cyan')
                                    abo_labels[14].place(x=250, y=112)

                        def start():
                            global play_state, q, play_num, model, num, multiplayer_mode, connection

                            if play_num == 3:
                                win6 = tk.Toplevel(win3)
                                win6.geometry('220x200+100+100')
                                win6.title('联机方式')
                                win6.resizable(False, False)
                                win6.configure(bg='light cyan')

                                def select_local():
                                    global multiplayer_mode
                                    multiplayer_mode = 0
                                    win6.destroy()
                                    start_game()

                                def select_host():
                                    global multiplayer_mode, ws_conn, room_id
                                    multiplayer_mode = 1
                                    room_id = simpledialog.askstring('创建房间', '设置房间号')
                                    if not room_id or ' ' in room_id:
                                        multiplayer_mode = 0
                                        return
                                    room_pw = simpledialog.askstring('创建房间', '设置房间密码（留空=不设密码）')
                                    if room_pw is None:
                                        multiplayer_mode = 0
                                        return
                                    try:
                                        ws_conn = websocket.create_connection(_ws_url(room_id, room_pw))
                                        ws_conn.send(json.dumps({'action': 'join', 'room': room_id}))
                                        win6.destroy()
                                        messagebox.showinfo('等待中', f'房间号：{room_id}\n等待对手加入...')
                                        while True:
                                            info = json.loads(ws_conn.recv())
                                            if info.get('type') == 'room_info' and info.get('count', 0) >= 2:
                                                break
                                        messagebox.showinfo('已连接', '对手已加入')
                                        start_game()
                                        threading.Thread(target=ws_receive_loop, args=(win3,), daemon=True).start()
                                    except Exception as e:
                                        messagebox.showerror(eng_chn_li[112][eng_chn],
                                                             f'{eng_chn_li[92][eng_chn]}: {_ws_err(e)}')
                                        multiplayer_mode = 0

                                def select_client():
                                    global multiplayer_mode, ws_conn, room_id
                                    multiplayer_mode = 2
                                    room_id = simpledialog.askstring('加入房间', '输入房主的房间号')
                                    if not room_id:
                                        multiplayer_mode = 0
                                        return
                                    room_pw = simpledialog.askstring('加入房间', '房间密码（房主没设就留空）')
                                    if room_pw is None:
                                        multiplayer_mode = 0
                                        return
                                    try:
                                        ws_conn = websocket.create_connection(_ws_url(room_id, room_pw))
                                        ws_conn.send(json.dumps({'action': 'join', 'room': room_id}))
                                        win6.destroy()
                                        messagebox.showinfo('已连接', '已加入房间')
                                        start_game()
                                        threading.Thread(target=ws_receive_loop, args=(win3,), daemon=True).start()
                                    except Exception as e:
                                        messagebox.showerror(eng_chn_li[112][eng_chn],
                                                             f'{eng_chn_li[94][eng_chn]}: {_ws_err(e)}')
                                        multiplayer_mode = 0

                                tk.Label(win6, text='选择联机方式', bg='light cyan',
                                         font=font.Font(family=pf, size=15)).place(x=50, y=10)
                                tk.Button(win6, text='线下对战', width=15, command=select_local,
                                          font=font.Font(family=pz, size=12), bg='deepskyblue').place(x=20, y=50)
                                tk.Button(win6, text='创建房间', width=15, command=select_host,
                                          font=font.Font(family=pz, size=12), bg='deepskyblue').place(x=20, y=95)
                                tk.Button(win6, text='加入房间', width=15, command=select_client,
                                          font=font.Font(family=pz, size=12), bg='deepskyblue').place(x=20, y=140)
                                win6.mainloop()
                            else:
                                start_game()

                        def start_game():
                            global play_state, q, play_num, model, num
                            model = combo.get()
                            for i in range(1,122):
                                cn_buttons[i].config(text='')
                                q = [[0 for _ in range(11)] for _ in range(11)]
                            play_state = 1
                            num = 0
                            if play_num == 2:
                                num = rd.choice([[5, 5], [4, 4], [4, 6], [6, 4], [6, 6], [5, 5], [5, 5], [5, 5]])
                                q[num[0]][num[1]] = 2
                                print(q)
                                cn_buttons[num[0]*11+num[1]+1].config(text='○')
                            if play_num == 3 and multiplayer_mode == 2:  # 客户端先等待主机下棋
                                cn_buttons[122].config(text=eng_chn_li[105][eng_chn])

                        def ECH2():
                            global eng_chn
                            if eng_chn == 0:
                                eng_chn = 1
                            elif eng_chn == 1:
                                eng_chn = 0
                            global up_state, ms, st
                            if up_state == 0:
                                for i in range(1,124):  #Θ◎
                                    cn_buttons[i].destroy()
                            if up_state == 2:
                                for i in range(15):
                                    abo_labels[i].destroy()
                            if up_state == 1:
                                for i in range(26):  #Θ◎
                                    d_labels[i].destroy()
                            up_state=0
                            win3.destroy()
                            f1 = open('files_old\\YQ_DataBase.json', 'r')
                            ms = json.loads(f1.read())
                            f1.close()
                            run_CCS()
                        fs= tk.Canvas(win3,width=500,height=4,bg='black', highlightbackground='light cyan')
                        fs.place(x=-5,y=38+65)
                        de_buttons[1] = tk.Button(win3, command=lambda arg=1:change_nums(arg), width=9,height=2, text=eng_chn_li[120][eng_chn], font=font.Font(family=ph,size=10),activebackground='whitesmoke',bg='whitesmoke')
                        de_buttons[1].place(x=0, y=70)
                        de_buttons[2] = tk.Button(win3, command=lambda arg=2:change_nums(arg), width=9,height=2, text=eng_chn_li[121][eng_chn], font=font.Font(family=ph,size=10),activebackground='deepskyblue',bg='deepskyblue')
                        de_buttons[2].place(x=73, y=70)
                        de_buttons[3] = tk.Button(win3, command=lambda arg=3:change_nums(arg), width=9,height=2, text=eng_chn_li[122][eng_chn], font=font.Font(family=ph,size=10),activebackground='deepskyblue',bg='deepskyblue')
                        de_buttons[3].place(x=73*2, y=70)
                        de_buttons[4] = tk.Button(win3, command=lambda arg=4:change_nums(arg), width=9,height=2, text=eng_chn_li[123][eng_chn], font=font.Font(family=ph,size=10),activebackground='deepskyblue',bg='deepskyblue')
                        de_buttons[4].place(x=73*3, y=70)
                        de_buttons[5] = tk.Button(win3, command=lambda arg=5:change_nums(arg), width=9,height=2, text=eng_chn_li[124][eng_chn], font=font.Font(family=ph,size=10),activebackground='deepskyblue',bg='deepskyblue')
                        de_buttons[5].place(x=73*4, y=70)

                        combo = ttk.Combobox(win3, width=15, values=['NW4.3-M100','NW4.3-M200','NW4.3-M400','NW4.3-M800'])
                        combo.place(x=230, y=5)
                        combo.current(1)
                        bg_img = Image.open('images\\云棋AI-BG1.png')
                        crop_bg = bg_img.crop((200, 40, 320, 60))
                        crop_bg_tk = ImageTk.PhotoImage(crop_bg)

                        cv = tk.Canvas(win3, width=120, height=20, highlightthickness=0, bd=0)
                        cv.place(x=200, y=40)
                        cv.create_image(0, 0, image=crop_bg_tk, anchor='nw')
                        cv.image = crop_bg_tk
                        color_list = ['#2E8B57', '#800080', '#FFC0CB','#4169E1', '#CD5C5C', '#00FF00', '#FFD700', '#7B68EE', '#C0C0C0', '#00FFFF']
                        def choose(level):
                            if level < 11: return '⬆'
                            elif level < 21: return '◆'
                            else: return '★'
                        cv.create_text(60, 10, text=choose(person['level'])+'Lv.'+str(person['level']), fill=color_list[(person['level']-1)%10],
                                       font=font.Font(family=pz, size=14, weight='bold'))

                        rc_y = 150
                        for j in range(1, 12):
                            for i in range(1, 12):
                                cn_buttons[(j-1)*11+i] = tk.Button(win3,width=2,height=1,activebackground='yellow', command=lambda arg=(j-1)*11+i:change_C(arg),font=font.Font(family=ph,size=13),bg='yellow')
                                cn_buttons[(j-1)*11+i].place(x=(i-1)*30+20,y=rc_y)
                            rc_y+=30
                        cn_buttons[122] = tk.Label(win3,text=eng_chn_li[24][eng_chn],font=font.Font(family=pz,size=13),bg='light cyan')
                        cn_buttons[122].place(x=60,y=125)
                        cn_buttons[123] = tk.Button(win3, command=start, width=10,height=1, text=eng_chn_li[23][eng_chn], font=font.Font(family=pz,size=15),activebackground='yellow',bg='yellow')
                        cn_buttons[123].place(x=110, y=488)
                        about_me= tk.Label(win3, text='◎'+eng_chn_li[0][eng_chn],bg='light cyan',fg='gray', font=font.Font(family=pf,size=10))
                        about_me.place(x=10, y=530)
                        chg = tk.Button(win3, command=ECH2, width=8, text=eng_chn_li[114][eng_chn], font=font.Font(family=pf,size=10),activebackground='whitesmoke',bg='whitesmoke')
                        chg.place(x=290, y=525)
                        win3.mainloop()
                    win.destroy()
                    run_CCS()
                else:
                    if s_n != 1:
                        s_n -= 1
                        messagebox.showerror(eng_chn_li[14][eng_chn], eng_chn_li[21][eng_chn]+str(s_n)+eng_chn_li[22][eng_chn])
                    else:
                        win.destroy()
            else:
                messagebox.showinfo(eng_chn_li[14][eng_chn], eng_chn_li[20][eng_chn])
        else:
            messagebox.showwarning(eng_chn_li[14][eng_chn], eng_chn_li[17][eng_chn])

    def make_new():
        win4 = tk.Toplevel()
        win4.geometry('320x390+100+100')
        win4.title(eng_chn_li[12][eng_chn])
        win4.configure(bg='light cyan')
        win4.resizable(False,False)
        win4.iconbitmap('images\\云棋AI.ico')

        global img, img2
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
            if not(name2.get =='' or mm.get() == '' or mm2.get() == ''):
                if name2.get() not in ms.keys():
                    if mm.get() == mm2.get():
                        if mm.get().isnumeric() or mm.get().isalpha() or len(mm.get()) < 5 or not mm.get().isalnum():
                            messagebox.showwarning(eng_chn_li[14][eng_chn], eng_chn_li[19][eng_chn])
                        else:
                            f1 = open('files_old\\YQ_DataBase.json', 'w')
                            t1, t2 = str(dt.datetime.now())[:10], str(dt.datetime.now())[-6:]
                            t3 = ''.join(t1.split('-'))
                            t4 = "YH"+t3+t2
                            sal, pasw = hash(mm.get())
                            ms[name2.get()] = {'photo':'','name':name2.get(),'password':f'{sal}:{pasw}','password_length':len(mm.get()),'ID':t4,'win_num':0, 'YH_number':0,'level':1,'english_type':eng_chn,'connect_list':[],'game_num':0,'lose_num':0,'beat_hard':0,'online_num':0,'cj_win':0,'cj_done':[],'lian_win_max':0,'lian_win_now':0}
                            f1.writelines(json.dumps(ms))
                            with open('files_old\\history.json', 'r') as f3:
                                rrs = json.loads(f3.read())
                            rrs[name2.get()] = {}
                            with open('files_old\\history.json', 'w') as f4:
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
    ask = tk.Label(win, text=eng_chn_li[5][eng_chn],bg='light cyan', font=font.Font(family=pf,size=15))
    ask.place(x=20, y=80)
    name = tk.Label(win, text=eng_chn_li[6][eng_chn],bg='light cyan', font=font.Font(family=pf,size=16))
    name.place(x=20, y=130)
    name2 = tk.Entry(win,width=20,font=font.Font(family=pf,size=16))
    name2.place(x=20, y=170)
    name = tk.Label(win, text=eng_chn_li[7][eng_chn],bg='light cyan', font=font.Font(family=pf,size=16))
    name.place(x=20, y=210)
    mm = tk.Entry(win,width=15, font=font.Font(family=pf,size=16), show='•')
    mm.place(x=20, y=250)
    de = tk.Button(win, command=change, width=5, text=eng_chn_li[2][eng_chn], font=font.Font(family=pf,size=10),activebackground='whitesmoke',bg='whitesmoke')
    de.place(x=200, y=250)
    get = tk.Button(win, command=cstart, width=10, text=eng_chn_li[8][eng_chn], font=font.Font(family=pf,size=15),activebackground='whitesmoke',bg='whitesmoke')
    get.place(x=35, y=290)
    get2 = tk.Button(win, command=make_new, width=10,height=1, text=eng_chn_li[9][eng_chn], font=font.Font(family=pf,size=15),activebackground='whitesmoke',bg='whitesmoke')
    get2.place(x=155, y=290)
    about_me = tk.Label(win, text='◎'+eng_chn_li[0][eng_chn],bg='light cyan',fg='grey', font=font.Font(family=pf,size=9))
    about_me.place(x=5, y=340)
    chg = tk.Button(win, command=eng_chn_chg, width=8, text=eng_chn_li[114][eng_chn], font=font.Font(family=pf,size=10),activebackground='whitesmoke',bg='whitesmoke')
    chg.place(x=250, y=345)
    win.mainloop()

if __name__ == "__main__":
    start_win()