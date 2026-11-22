# 联机配置：整个项目只有这一处需要改
#
# 公网联机（正常玩就用这个）
WS_URL = 'wss://cloudchess.dpdns.org'

# 本地调试：注释掉上面一行，改用下面这行（注意是 ws:// 不是 wss://，端口对应 pywrangler dev）
# WS_URL = 'ws://127.0.0.1:8787'

# 只写到域名，不要带 /room/，也不要带结尾斜杠
# 房号和密码由 files/network/ws_client.py 自动拼接并做 URL 编码

CONNECT_TIMEOUT = 15     # 握手超时（秒）
HEARTBEAT_INTERVAL = 45  # 心跳间隔（秒），防止 Cloudflare 掐断空闲连接

# 以下由 ws_client.py 在运行时写入，仅用于调试查看，不用手动改
connection = None
room_id = ''
ws_conn = None
server = '12345'
