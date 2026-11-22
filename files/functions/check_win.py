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