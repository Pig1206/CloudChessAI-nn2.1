import tkinter as tk
from tkinter import ttk, font, messagebox

import json

from files.config.parameters import params
from files.config.CN_EN import eng_chn_li
from files.config.fonts import ph, pf

eng_chn = params.eng_chn
person = params.person

class History:
    def __init__(self):
        self.hist_win = tk.Toplevel()
        self.hist_win.geometry('600x530+250+150')
        self.hist_win.title(eng_chn_li[47][eng_chn])
        self.hist_win.configure(bg='light cyan')
        self.hist_win.resizable(False, False)

        self.hist_win.after(0, self.draw)

        self.hist_win.mainloop()
    def draw(self):
        tk.Label(self.hist_win, text=eng_chn_li[48][eng_chn], bg='light cyan', font=font.Font(family=pf, size=12)).place(
            x=20, y=20)
        self.date_entry = tk.Entry(self.hist_win, width=15, font=font.Font(family=pf, size=12))
        self.date_entry.place(x=100, y=20)

        tk.Label(self.hist_win, text=eng_chn_li[49][eng_chn], bg='light cyan', font=font.Font(family=pf, size=12)).place(
            x=250, y=20)
        self.type_combo = ttk.Combobox(self.hist_win, width=15,
                                  values=[eng_chn_li[49][eng_chn], 'AI', 'me', 'player1', 'player2', 'other'])
        self.type_combo.place(x=330, y=20)
        self.type_combo.current(0)

        tk.Button(self.hist_win, text=eng_chn_li[50][eng_chn], command=self.query, width=8, font=font.Font(family=pf, size=12),
                  bg='whitesmoke').place(x=480, y=17)


        columns = (eng_chn_li[51][eng_chn], eng_chn_li[52][eng_chn], eng_chn_li[53][eng_chn])
        self.tree = ttk.Treeview(self.hist_win, columns=columns, show='headings', height=18)
        self.tree.heading(eng_chn_li[51][eng_chn], text=eng_chn_li[51][eng_chn])
        self.tree.heading(eng_chn_li[52][eng_chn], text=eng_chn_li[52][eng_chn])
        self.tree.heading(eng_chn_li[53][eng_chn], text=eng_chn_li[53][eng_chn])
        self.tree.column(eng_chn_li[51][eng_chn], width=150)
        self.tree.column(eng_chn_li[52][eng_chn], width=260)
        self.tree.column(eng_chn_li[53][eng_chn], width=140)
        self.tree.place(x=20, y=70)

        scrollbar = ttk.Scrollbar(self.hist_win, orient='vertical', command=self.tree.yview)
        scrollbar.place(x=573, y=70, height=380)
        self.tree.configure(yscrollcommand=scrollbar.set)

        tk.Button(self.hist_win, text=eng_chn_li[54][eng_chn], command=self.delete_selected, width=8,
                  font=font.Font(family=pf, size=12), bg='whitesmoke').place(x=20, y=460)
        tk.Button(self.hist_win, text=eng_chn_li[55][eng_chn], command=self.delete_all, width=8,
                  font=font.Font(family=pf, size=12), bg='whitesmoke').place(x=120, y=460)

        about_me = tk.Label(self.hist_win, text='◎' + eng_chn_li[0][eng_chn], bg='light cyan', fg='gray',
                            font=font.Font(family=pf, size=10))
        about_me.place(x=10, y=500)

        self.tree.bind('<Double-1>', self.show_board)
        self.update_tree()

    def query(self):
        self.update_tree()

    def load_history(self):
        try:
            with open('files\\history.json', 'r') as f:
                data = json.load(f)
                return data.get(person['name'], {})
        except:
            return {}

    def save_history(self,history_data):
        try:
            with open('files\\history.json', 'r') as f:
                all_data = json.load(f)
        except:
            all_data = {}

        all_data[person['name']] = history_data
        with open('files\\history.json', 'w') as f:
            f.write(json.dumps(all_data))

    def update_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        history = self.load_history()
        date_filter = self.date_entry.get()
        type_filter = self.type_combo.get()

        for board_str, info in history.items():
            play_type = info[0]
            play_time = info[1]

            if date_filter and date_filter not in play_time[:10]:
                continue
            if type_filter != eng_chn_li[49][eng_chn] and type_filter != play_type:
                continue

            board_preview = board_str[:50] + '...' if len(board_str) > 50 else board_str
            self.tree.insert('', 'end', values=(play_time[:19], board_preview, play_type), tags=(board_str,))

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(eng_chn_li[39][eng_chn], eng_chn_li[56][eng_chn])
            return

        if messagebox.askyesno(eng_chn_li[54][eng_chn], eng_chn_li[57][eng_chn]):
            history = self.load_history()
            for item in selected:
                board_str = self.tree.item(item, 'tags')[0]
                if board_str in history:
                    del history[board_str]
            self.save_history(history)
            self.update_tree()
            messagebox.showinfo(eng_chn_li[14][eng_chn], eng_chn_li[58][eng_chn])

    def delete_all(self):
        if messagebox.askyesno(eng_chn_li[55][eng_chn], eng_chn_li[59][eng_chn]):
            self.save_history({})
            self.update_tree()
            messagebox.showinfo(eng_chn_li[14][eng_chn], eng_chn_li[60][eng_chn])

    def show_board(self,event):
        item = self.tree.selection()[0]
        board_str = self.tree.item(item, 'tags')[0]

        try:
            board = eval(board_str)
        except:
            return

        board_win = tk.Toplevel(self.hist_win)
        board_win.geometry('400x430+300+200')
        board_win.title(eng_chn_li[61][eng_chn])
        board_win.configure(bg='yellow')
        board_win.resizable(False, False)

        for i in range(11):
            for j in range(11):
                x, y = j * 30 + 30, i * 30 + 50
                if board[i][j] == 1:
                    tk.Label(board_win, text='●', font=font.Font(family=ph, size=15), bg='yellow').place(x=x, y=y)
                elif board[i][j] == 2:
                    tk.Label(board_win, text='○', font=font.Font(family=ph, size=15), bg='yellow').place(x=x, y=y)
                else:
                    tk.Label(board_win, text='·', font=font.Font(family=ph, size=15), bg='yellow').place(x=x, y=y)
