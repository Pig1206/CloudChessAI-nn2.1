import json
import os

from files.config.paths_parameters import files_path


class Parameters():
    def __init__(self):
        self.bg = 'yellow'  # 背景色
        self.num = 0  # 步数计数器
        self.q = [[0 for _ in range(11)] for _ in range(11)]  # 棋盘状态
        self.s_n = 4  # 剩余登录尝试次数
        self.play_num = 1  # 游戏模式（1-AI先手，2-AI后手，3-双人）
        self.play_state = 0  # 游戏状态（0-未开始，1-进行中）
        self.num2_state = 0  # 双人模式回合状态
        self.up_state = 0  # 界面状态（0-主界面，1-个人信息，2-关于）
        self.eng_chn = 0  # 语言切换
        self.person = {}  # 当前登录用户信息
        self.model = 'NW-M800'  # 模型选择（兼容旧代码）
        self.multiplayer_mode = 0  # 0-线下对战, 1-联机对战(主机), 2-联机对战(客户端)

        # AI参数设置
        self.ai_params = {
            'n_sim': 800,
            'c_puct': 1.0,
            'temp': 0.1,
            'n_threads': 4,
            'vl_weight': 0.5,
            'use_opp_model': False,
            'opp_weight': 0.3
        }

        # 加载全局 parameter.json
        self.param_json_path = os.path.join(files_path,'parameter.json')
        self.all_ai_params = {}
        self.load_all_ai_params()

    def load_all_ai_params(self):
        if os.path.exists(self.param_json_path):
            try:
                with open(self.param_json_path, 'r', encoding='utf-8') as f:
                    self.all_ai_params = json.load(f)
            except:
                self.all_ai_params = {}

    def load_user_ai_params(self, username):
        if username in self.all_ai_params:
            self.ai_params.update(self.all_ai_params[username])
        else:
            self.ai_params = {
                'n_sim': 800, 'c_puct': 1.0, 'temp': 0.1,
                'n_threads': 4, 'vl_weight': 0.5,
                'use_opp_model': False, 'opp_weight': 0.3
            }

    def save_user_ai_params(self, username):
        self.all_ai_params[username] = self.ai_params
        os.makedirs(os.path.dirname(self.param_json_path), exist_ok=True)
        with open(self.param_json_path, 'w', encoding='utf-8') as f:
            json.dump(self.all_ai_params, f, ensure_ascii=False, indent=4)


cj_list = [
            {'name': '初出茅庐', 'desc': '完成第一局对局', 'type': 'game_num', 'goal': 1, 'reward': '云币+5'},
            {'name': '百战老将', 'desc': '累计完成100局对局', 'type': 'game_num', 'goal': 100, 'reward': '云币+20'},
            {'name': '首胜之光', 'desc': '获得第一场胜利', 'type': 'win_num', 'goal': 1, 'reward': '云币+5'},
            {'name': '常胜将军', 'desc': '累计获胜50次', 'type': 'win_num', 'goal': 50, 'reward': '云币+30'},
            {'name': '棋圣降世', 'desc': '累计获胜200次', 'type': 'win_num', 'goal': 200, 'reward': '云币+66'},
            {'name': '破产边缘', 'desc': '累计失败30局', 'type': 'lose_num', 'goal': 30, 'reward': '云币+20'},
            {'name': 'AI克星', 'desc': '在NW-M1600难度下战胜AI', 'type': 'beat_hard', 'goal': 1, 'reward': '云币+5'},
            {'name': '社交达人', 'desc': '完成一次联机对战', 'type': 'online_num', 'goal': 1, 'reward': '云币+5'},
            {'name': '残局高手', 'desc': '破解10个残局', 'type': 'cj_win', 'goal': 10, 'reward': '云币+10'},
            {'name': '残局大师', 'desc': '破解30个残局', 'type': 'cj_win', 'goal': 30, 'reward': '云币+25'},
            {'name': '十连胜', 'desc': '连胜10局', 'type': 'lian_win', 'goal': 10, 'reward': '云币+35'},
            {'name': '等级飞升', 'desc': '达到Lv.10', 'type': 'level10', 'goal': 1, 'reward': '云币+30'},
        ]

params = Parameters()
