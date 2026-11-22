"""云棋AI 联机客户端 (适配 Cloudflare Worker 版)"""

import json
import threading
from urllib.parse import quote
import websocket


WS_URL = "wss://cloudchess.dpdns.org"
# ==============================

ERR_AUTH = 'auth'          # 403 密码错误
ERR_FULL = 'full'          # 409 房间已满
ERR_BAD_ROOM = 'bad_room'  # 400 房号不合法
ERR_NET = 'net'            # 连不上、超时、域名不通

CONNECT_TIMEOUT = 15
HEARTBEAT_INTERVAL = 45

class NetError(Exception):
    def __init__(self, message, code=ERR_NET):
        super().__init__(message)
        self.code = code

def _classify(exc):
    s = str(exc).lower()
    if '403' in s: return ERR_AUTH
    if '409' in s: return ERR_FULL
    if '400' in s: return ERR_BAD_ROOM
    return ERR_NET

class NetClient():
    def __init__(self, on_event=None):
        self.on_event = on_event or (lambda kind, data: None)
        self._ws = None
        self._room = ''
        self._running = False
        self._thread = None
        self._hb_thread = None
        self._closed_by_me = False

    @property
    def room(self):
        return self._room

    def build_url(self, room, pw=''):
        """拼接请求地址，与 Worker 的 /room/{roomId}?pw={password} 路由匹配"""
        url = f'{WS_URL}/room/{quote(str(room), safe="")}'
        if pw:
            url += '?pw=' + quote(str(pw), safe='')
        return url

    def connect(self, room, pw=''):
        if self._ws is not None:
            self.close()
        self._closed_by_me = False

        # 打印出来方便调试，确认连的是对的地址
        print(f"正在连接服务器: {self.build_url(room, pw)}")

        try:
            ws = websocket.create_connection(
                self.build_url(room, pw),
                timeout=CONNECT_TIMEOUT,
                enable_multithread=True,
            )
        except Exception as e:
            raise NetError(str(e), _classify(e)) from e

        try:
            ws.settimeout(None)
        except Exception:
            pass

        self._ws = ws
        self._room = room
        self._running = True

        self._thread = threading.Thread(target=self._recv_loop, daemon=True)
        self._thread.start()
        self._hb_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._hb_thread.start()

    def send_move(self, n):
        if not self._ws:
            return False
        try:
            self._ws.send(json.dumps({'action': 'move', 'room': self._room, 'n': n}))
            return True
        except Exception:
            return False

    def close(self):
        self._closed_by_me = True
        self._running = False
        ws, self._ws = self._ws, None
        if ws is not None:
            try:
                ws.close()
            except Exception:
                pass

    def _recv_loop(self):
        while self._running and self._ws:
            try:
                raw = self._ws.recv()
            except Exception:
                break
            if not raw:
                break
            try:
                data = json.loads(raw)
            except Exception:
                continue
            if not isinstance(data, dict):
                continue

            kind = data.get('type')
            if kind == 'move':
                self.on_event('move', data.get('n'))
            elif kind == 'room_info':
                self.on_event('room_info', data.get('count', 0))
            elif kind == 'opponent_left':
                self.on_event('left', data.get('count', 0))

        self._running = False
        if not self._closed_by_me:
            self.on_event('closed', None)

    def _heartbeat_loop(self):
        while self._running:
            threading.Event().wait(HEARTBEAT_INTERVAL)
            if not self._running or not self._ws:
                break
            try:
                self._ws.ping()
            except Exception:
                break