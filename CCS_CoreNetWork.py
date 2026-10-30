import torch
import torch.nn as nn
import numpy as np
import math, os, random, json
import threading
from collections import defaultdict


# ==================== 网络定义 ====================
class PolicyNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=5, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),
            nn.Dropout2d(0.2),

            nn.Conv2d(16, 32, kernel_size=5, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.Dropout2d(0.25),

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Dropout2d(0.2),

            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.Dropout2d(0.1),

            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.Dropout2d(0.1)
        )
        self.fc = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * 7 * 7, 128),
            nn.ReLU(),
            nn.Dropout(0.60),

            nn.Linear(128, 121)
        )

    def forward(self, x):
        x = x.unsqueeze(1)
        x = self.conv(x)
        x = self.fc(x)
        return x


class ValueNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(1, 16, kernel_size=5, padding=1),
            nn.BatchNorm2d(16),
            nn.ReLU(),

            nn.Conv2d(16, 32, kernel_size=5, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),

            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU()
        )
        self.fc = nn.Sequential(
            nn.AvgPool2d(2),
            nn.Flatten(),

            nn.Linear(64 * 3 * 3, 32),
            nn.ReLU(),
            nn.Dropout(0.6),

            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        x = x.unsqueeze(1)
        x = self.conv(x)
        x = self.fc(x)
        return x.squeeze(-1)


# ==================== 棋盘工具 ====================
def encode(board):
    return np.asarray(board, dtype=np.float32)


def legal_moves(board):
    arr = np.asarray(board)
    return np.flatnonzero(arr.ravel() == 0).tolist()


def check_win(board, player):
    b = np.asarray(board)
    for dx, dy in ((0, 1), (1, 0), (1, 1), (1, -1)):
        for i in range(11):
            for j in range(11):
                if b[i, j] != player:
                    continue
                cnt = 1
                for k in range(1, 5):
                    ni, nj = i + dx * k, j + dy * k
                    if 0 <= ni < 11 and 0 <= nj < 11 and b[ni, nj] == player:
                        cnt += 1
                    else:
                        break
                if cnt >= 5:
                    return True
    return False


# ==================== 对手模型 ====================
def build_opponent_model(history_path, username):
    """
    从历史记录统计对手走法偏好

    返回:
        opponent_model: dict, key=棋盘字符串, value={走法: 次数}
    """
    opponent_model = defaultdict(lambda: defaultdict(int))

    if not os.path.exists(history_path):
        return opponent_model

    with open(history_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    user_history = data.get(username, {})

    for key, value in user_history.items():
        if isinstance(value, dict) and 'moves' in value:
            for entry in value['moves']:
                board = entry.get('board')
                move = entry.get('move')
                player = entry.get('player')
                if board is not None and move is not None and player == 1:
                    opponent_model[str(board)][tuple(move)] += 1

    return opponent_model


# ==================== MCTS 节点 ====================
class Node:
    __slots__ = ('board', 'player', 'parent', 'prob', 'children', 'N', 'W', 'Q', 'vl')

    def __init__(self, board, player, parent=None, prob=0.0):
        self.board = board
        self.player = player
        self.parent = parent
        self.prob = prob
        self.children = {}
        self.N = 0
        self.W = 0.0
        self.Q = 0.0
        self.vl = 0


# ==================== MCTS 搜索 ====================
class MCTS:
    def __init__(self, policy, value, c_puct=1.0, n_sim=400, normal_state=True, sigma=0.001,
                 vl_weight=0.5, temperature=0.1, fpu_enable=True, n_threads=4,
                 opponent_model=None, opp_weight=0.3):
        self.policy = policy
        self.value = value
        self.c_puct = c_puct
        self.n_sim = n_sim
        self.device = next(policy.parameters()).device
        self.open_normal = normal_state
        self.sigma = sigma
        self.vl_weight = vl_weight
        self.temperature = temperature
        self.fpu_enable = fpu_enable
        self.n_threads = n_threads
        self.opponent_model = opponent_model
        self.opp_weight = opp_weight
        self.lock = threading.Lock()

    def _eval(self, board):
        x = torch.from_numpy(encode(board)).unsqueeze(0).to(self.device)
        with torch.no_grad():
            logits = self.policy(x)
            probs = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()
            val = self.value(x).item()
        return probs, val

    def _opponent_bias(self, board, move):
        """计算对手走法的偏好权重"""
        if not self.opponent_model:
            return 0.5

        board_key = str(board)
        if board_key not in self.opponent_model:
            return 0.5

        move_counts = self.opponent_model[board_key]
        total = sum(move_counts.values())
        if total == 0:
            return 0.5

        count = move_counts.get(tuple(move), 0)
        return count / total

    def _select(self, node):
        if self.fpu_enable:
            visited_q = [c.Q for c in node.children.values() if c.N > 0]
            fpu = sum(visited_q) / len(visited_q) if visited_q else 0.5
        else:
            fpu = 0.0

        best, best_score = None, -1e9
        sqrt_n = math.sqrt(node.N)
        for move, child in node.children.items():
            q = child.Q if child.N > 0 else fpu
            u = self.c_puct * child.prob * sqrt_n / (1 + child.N)
            score = q + u - self.vl_weight * child.vl
            if self.open_normal:
                score += np.random.normal(0, self.sigma)
            if score > best_score:
                best_score, best = score, child
        best.vl += 1
        return best

    def _expand(self, node):
        moves = legal_moves(node.board)
        if not moves:
            return 0.0

        probs, val = self._eval(node.board)
        p_sum = float(probs[moves].sum())
        board_arr = np.asarray(node.board)

        for m in moves:
            p = probs[m] / p_sum if p_sum > 0 else 1.0 / len(moves)

            # 对手模型加权
            if node.player == 1 and self.opponent_model:
                bias = self._opponent_bias(node.board, (m // 11, m % 11))
                p = (1 - self.opp_weight) * p + self.opp_weight * bias

            nb = board_arr.copy()
            nb[m // 11, m % 11] = node.player
            node.children[m] = Node(nb.tolist(), 3 - node.player, node, float(p))

        return val

    def _backprop(self, node, val):
        while node:
            node.N += 1
            if node.player == 1:
                node.W += (1 - val)
            else:
                node.W += val
            node.Q = node.W / node.N
            node.vl = max(0, node.vl - 1)
            node = node.parent

    def _simulate(self, root):
        node = root
        while node.children:
            node = self._select(node)
        if check_win(node.board, 3 - node.player):
            val = 0.0 if node.player == 1 else 1.0
        else:
            val = self._expand(node)
        self._backprop(node, val)

    def _run_thread(self, root, n_sim):
        for _ in range(n_sim):
            self._simulate(root)

    def search(self, board, player):
        board_arr = np.asarray(board)
        stones = np.count_nonzero(board_arr)

        # 开局阶段：中心附近
        if stones <= 1:
            candidates = [
                5 * 11 + 5,
                4 * 11 + 5,
                5 * 11 + 4,
                5 * 11 + 6,
                6 * 11 + 5,
                4 * 11 + 4,
                4 * 11 + 6,
                6 * 11 + 4,
                6 * 11 + 6,
            ]
            legal = legal_moves(board)
            candidates = [m for m in candidates if m in legal]
            if candidates:
                return random.choice(candidates)

        # 必胜检测
        for m in legal_moves(board):
            nb = board_arr.copy()
            nb[m // 11, m % 11] = player
            if check_win(nb.tolist(), player):
                return m

        # 必堵检测
        for m in legal_moves(board):
            nb = board_arr.copy()
            nb[m // 11, m % 11] = 3 - player
            if check_win(nb.tolist(), 3 - player):
                return m

        root = Node(board_arr.tolist(), player)

        # 根节点对手模型加权
        if player == 1 and self.opponent_model:
            board_key = str(board_arr.tolist())
            if board_key in self.opponent_model:
                move_counts = self.opponent_model[board_key]
                total = sum(move_counts.values())
                if total > 0:
                    for m in legal_moves(board):
                        bias = move_counts.get((m // 11, m % 11), 0) / total
                        if m not in root.children:
                            root.children[m] = Node(
                                (lambda nb: (nb.__setitem__((m // 11, m % 11), player), nb)[1])(
                                    board_arr.copy()).tolist(),
                                3 - player, root, 0.0
                            )
                        root.children[m].prob = (1 - self.opp_weight) * root.children[m].prob + self.opp_weight * bias

        # 多线程搜索
        n_per = self.n_sim // self.n_threads
        threads = []
        for _ in range(self.n_threads):
            t = threading.Thread(target=self._run_thread, args=(root, n_per))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()

        counts = {m: c.N for m, c in root.children.items()}

        if self.temperature < 0.01:
            return max(counts, key=counts.get)
        moves = list(counts.keys())
        weights = np.array([counts[m] ** (1.0 / self.temperature) for m in moves], dtype=np.float64)
        weights /= weights.sum()
        return int(np.random.choice(moves, p=weights))


# ==================== 模型加载 ====================
_device = None
_policy = None
_value = None
_loaded = False


def _load_models():
    global _device, _policy, _value, _loaded
    if _loaded:
        return
    _device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    _weight_dir = os.path.dirname(os.path.abspath(__file__))

    _policy = PolicyNet().to(_device)
    _policy.load_state_dict(
        torch.load(os.path.join(_weight_dir, 'CCS-PNN.pth'), map_location=_device)['model_state_dict']
    )
    _policy.eval()

    _value = ValueNet().to(_device)
    _value.load_state_dict(
        torch.load(os.path.join(_weight_dir, 'CCS-VNN.pth'), map_location=_device)['model_state_dict']
    )
    _value.eval()

    _loaded = True


def is_loaded():
    return _loaded


# ==================== 对外接口 ====================
class CCScore:
    def __init__(self, chess, difficulty=400, ai_player=2, ns=True, sigma=0.001,
                 vl_weight=0.5, temperature=0.1, fpu_enable=True, n_threads=4,
                 username=None, opp_weight=0.3, c_puct=1.0):
        _load_models()
        self.chess = chess
        self.difficulty = difficulty
        self.ai_player = ai_player
        self.n_sim = difficulty
        self.normal_state = ns
        self.sigma = sigma
        self.vl_weight = vl_weight
        self.temperature = temperature
        self.fpu_enable = fpu_enable
        self.n_threads = n_threads
        self.opp_weight = opp_weight
        self.c_puct = c_puct

        self.opponent_model = None
        if username:
            history_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'history.json')
            if os.path.exists(history_path):
                self.opponent_model = build_opponent_model(history_path, username)

    def find_best_move(self):
        mcts = MCTS(
            _policy, _value,
            c_puct=self.c_puct,
            n_sim=self.n_sim,
            normal_state=self.normal_state,
            sigma=self.sigma,
            vl_weight=self.vl_weight,
            temperature=self.temperature,
            fpu_enable=self.fpu_enable,
            n_threads=self.n_threads,
            opponent_model=self.opponent_model,
            opp_weight=self.opp_weight,
        )
        move = mcts.search(self.chess, player=self.ai_player)
        row, col = move // 11, move % 11
        return [col, row]