import tkinter as tk
from tkinter import messagebox
from tkinter import font

from files.config.parameters import params
from files.config.fonts import pz


class ParamAdjustWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.geometry('360x420+150+150')
        self.title('参数调整')
        self.configure(bg='light cyan')
        self.resizable(False, False)
        self.grab_set()

        self.ai_p = params.ai_params

        # 模拟次数
        lbl_nsim = tk.Label(self, text='模拟次数 (n_sim):', bg='light cyan', cursor='hand2')
        lbl_nsim.grid(row=0, column=0, sticky='e', padx=20, pady=12)
        lbl_nsim.bind('<Double-Button-1>', lambda e: self.show_info(
            "模拟次数 (n_sim)", "AI思考时推演的步数。\n数值越大，AI棋力越强，但计算时间越长。\n推荐值：400~1600"))

        self.ent_nsim = tk.Entry(self, width=12)
        self.ent_nsim.insert(0, str(self.ai_p.get('n_sim', 800)))
        self.ent_nsim.grid(row=0, column=1, sticky='w', padx=10, pady=12)

        # 探索系数
        lbl_cpuct = tk.Label(self, text='探索系数 (c_puct):', bg='light cyan', cursor='hand2')
        lbl_cpuct.grid(row=1, column=0, sticky='e', padx=20, pady=12)
        lbl_cpuct.bind('<Double-Button-1>', lambda e: self.show_info(
            "探索系数 (c_puct)", "控制探索与利用的平衡。\n数值越大，AI越喜欢尝试冷门走法；\n数值越小，AI越保守，只走当前认为最好的。\n推荐值：0.5~2.0"))

        self.ent_cpuct = tk.Entry(self, width=12)
        self.ent_cpuct.insert(0, str(self.ai_p.get('c_puct', 1.0)))
        self.ent_cpuct.grid(row=1, column=1, sticky='w', padx=10, pady=12)

        # 温度
        lbl_temp = tk.Label(self, text='温度 (temp):', bg='light cyan', cursor='hand2')
        lbl_temp.grid(row=2, column=0, sticky='e', padx=20, pady=12)
        lbl_temp.bind('<Double-Button-1>', lambda e: self.show_info(
            "温度 (temp)", "控制最终选子的随机性。\n数值越低，AI越大概率选择访问次数最多的最优解；\n数值越高，AI越容易选择次优解。\n实战推荐：0.01~0.2"))

        self.scale_temp = tk.Scale(self, from_=0.01, to=1.0, resolution=0.01, orient='horizontal', length=160,
                                   bg='light cyan', highlightthickness=0)
        self.scale_temp.set(self.ai_p.get('temp', 0.1))
        self.scale_temp.grid(row=2, column=1, sticky='w', padx=10, pady=12)

        # 线程数
        lbl_thread = tk.Label(self, text='线程数:', bg='light cyan', cursor='hand2')
        lbl_thread.grid(row=3, column=0, sticky='e', padx=20, pady=12)
        lbl_thread.bind('<Double-Button-1>', lambda e: self.show_info(
            "线程数", "AI多线程并行搜索的线程数量。\n建议设置为电脑 CPU 的核心数，核多调高可加速计算。\n推荐值：2~8"))

        self.scale_thread = tk.Scale(self, from_=1, to=8, resolution=1, orient='horizontal', length=160,
                                     bg='light cyan', highlightthickness=0)
        self.scale_thread.set(self.ai_p.get('n_threads', 4))
        self.scale_thread.grid(row=3, column=1, sticky='w', padx=10, pady=12)

        # 开启噪声
        self.var_noise = tk.BooleanVar(value=self.ai_p.get('sigma', 0.001) > 0)
        chk_noise = tk.Checkbutton(self, text='开启噪声', variable=self.var_noise, bg='light cyan', cursor='hand2',
                                   activebackground='light cyan')
        chk_noise.grid(row=4, column=0, columnspan=2, sticky='w', padx=60, pady=5)
        chk_noise.bind('<Double-Button-1>', lambda e: self.show_info(
            "开启噪声", "在评估节点时加入极小的随机波动，\n防止AI陷入固定的套路，增加搜索的多样性。"))

        # 启用对手模型
        self.var_opp = tk.BooleanVar(value=self.ai_p.get('use_opp_model', False))
        self.chk_opp = tk.Checkbutton(self, text='启用对手模型', variable=self.var_opp, bg='light cyan', cursor='hand2',
                                      activebackground='light cyan', command=self.toggle_opp_scale)
        self.chk_opp.grid(row=5, column=0, columnspan=2, sticky='w', padx=60, pady=5)
        self.chk_opp.bind('<Double-Button-1>', lambda e: self.show_info(
            "启用对手模型", "开启后，AI会读取你过往的对局历史，\n学习你的落子偏好，并专门针对你的习惯进行防守。"))

        # 模型系数
        lbl_opp = tk.Label(self, text='模型系数:', bg='light cyan', cursor='hand2')
        lbl_opp.grid(row=6, column=0, sticky='e', padx=20, pady=12)
        lbl_opp.bind('<Double-Button-1>', lambda e: self.show_info(
            "模型系数", "对手模型在AI决策中的权重。\n数值越高，AI越注重防守你的习惯；\n数值越低，AI越注重常规最优解。\n推荐值：0.2~0.5"))

        self.scale_opp_w = tk.Scale(self, from_=0.0, to=1.0, resolution=0.05, orient='horizontal', length=160,
                                    bg='light cyan', highlightthickness=0)
        self.scale_opp_w.set(self.ai_p.get('opp_weight', 0.3))
        self.scale_opp_w.grid(row=6, column=1, sticky='w', padx=10, pady=12)

        # 初始化滑杆状态
        self.toggle_opp_scale()

        # 保存
        tk.Button(self, text='保 存', command=self.save_and_close, width=12, bg='deepskyblue', font=font.Font(family=pz,size=12)).grid(
            row=7, column=0, columnspan=2, pady=25)

    def show_info(self, title, text):
        messagebox.showinfo(title, text, parent=self)

    def toggle_opp_scale(self):
        if self.var_opp.get():
            self.scale_opp_w.config(state='normal')
        else:
            self.scale_opp_w.config(state='disabled')

    def save_and_close(self):
        try:
            nsim = int(self.ent_nsim.get())
            cpuct = float(self.ent_cpuct.get())

            if nsim > 2000 and cpuct > 2.0:
                messagebox.showwarning("警告", "参数过大，可能会导致软件卡顿或无响应！", parent=self)

            params.ai_params['n_sim'] = nsim
            params.ai_params['c_puct'] = cpuct
            params.ai_params['temp'] = self.scale_temp.get()
            params.ai_params['n_threads'] = self.scale_thread.get()
            params.ai_params['sigma'] = 0.001 if self.var_noise.get() else 0.0
            params.ai_params['use_opp_model'] = self.var_opp.get()
            params.ai_params['opp_weight'] = self.scale_opp_w.get()

            if params.person and 'name' in params.person:
                params.save_user_ai_params(params.person['name'])

            self.destroy()
        except ValueError:
            messagebox.showerror("错误", "n_sim 必须为整数，c_puct 必须为浮点数！", parent=self)