import pygame

# 初始化 pygame
pygame.init()

# 创建窗口
screen = pygame.display.set_mode((800, 600))

# 棋盘参数
ROWS = 5
COLS = 5
CELL_SIZE = 80

BOARD_X = 200
BOARD_Y = 100


# 绘制箭头
def draw_arrow(screen, row, col, direction):
    # 计算当前格子的中心坐标
    center_x = BOARD_X + col * CELL_SIZE + CELL_SIZE // 2
    center_y = BOARD_Y + row * CELL_SIZE + CELL_SIZE // 2

    # 箭头主体长度
    body_length = 25

    # 箭头头部大小
    head_size = 10

    # 向右箭头
    if direction == "right":
        start = (center_x - body_length, center_y)
        end = (center_x + body_length, center_y)

        pygame.draw.line(
            screen,
            (0, 0, 0),
            start,
            end,
            4
        )

        pygame.draw.line(
            screen,
            (0, 0, 0),
            end,
            (end[0] - head_size, end[1] - head_size),
            4
        )

        pygame.draw.line(
            screen,
            (0, 0, 0),
            end,
            (end[0] - head_size, end[1] + head_size),
            4
        )

    # 向左箭头
    elif direction == "left":
        start = (center_x + body_length, center_y)
        end = (center_x - body_length, center_y)

        pygame.draw.line(
            screen,
            (0, 0, 0),
            start,
            end,
            4
        )

        pygame.draw.line(
            screen,
            (0, 0, 0),
            end,
            (end[0] + head_size, end[1] - head_size),
            4
        )

        pygame.draw.line(
            screen,
            (0, 0, 0),
            end,
            (end[0] + head_size, end[1] + head_size),
            4
        )

    # 向上箭头
    elif direction == "up":
        start = (center_x, center_y + body_length)
        end = (center_x, center_y - body_length)

        pygame.draw.line(
            screen,
            (0, 0, 0),
            start,
            end,
            4
        )

        pygame.draw.line(
            screen,
            (0, 0, 0),
            end,
            (end[0] - head_size, end[1] + head_size),
            4
        )

        pygame.draw.line(
            screen,
            (0, 0, 0),
            end,
            (end[0] + head_size, end[1] + head_size),
            4
        )

    # 向下箭头
    elif direction == "down":
        start = (center_x, center_y - body_length)
        end = (center_x, center_y + body_length)

        pygame.draw.line(
            screen,
            (0, 0, 0),
            start,
            end,
            4
        )

        pygame.draw.line(
            screen,
            (0, 0, 0),
            end,
            (end[0] - head_size, end[1] - head_size),
            4
        )

        pygame.draw.line(
            screen,
            (0, 0, 0),
            end,
            (end[0] + head_size, end[1] - head_size),
            4
        )


# 当前测试用的箭头数据
arrows = [
    {"row": 0, "col": 0, "direction": "right"},
    {"row": 1, "col": 3, "direction": "down"},
    {"row": 3, "col": 1, "direction": "left"},
    {"row": 4, "col": 4, "direction": "up"}
]


# 根据行列位置查找箭头
def find_arrow(row, col):
    # 依次检查 arrows 中的每一个箭头
    for arrow in arrows:

        # 如果这个箭头的行和列都与点击位置相同
        if arrow["row"] == row and arrow["col"] == col:
            return arrow

    # 如果全部检查完都没有找到
    return None


# 控制游戏是否继续运行
running = True

# 游戏主循环
while running:

    # 获取当前所有事件
    for event in pygame.event.get():

        # 点击窗口关闭按钮
        if event.type == pygame.QUIT:
            running = False

        # 鼠标按下
        if event.type == pygame.MOUSEBUTTONDOWN:

            # 获取鼠标点击位置
            mouse_x, mouse_y = event.pos

            # 判断鼠标是否点击在棋盘内部
            if (
                BOARD_X <= mouse_x < BOARD_X + COLS * CELL_SIZE
                and
                BOARD_Y <= mouse_y < BOARD_Y + ROWS * CELL_SIZE
            ):

                # 把屏幕坐标转换成棋盘中的行列坐标
                col = (mouse_x - BOARD_X) // CELL_SIZE
                row = (mouse_y - BOARD_Y) // CELL_SIZE

                # 查找这个格子里是否存在箭头
                clicked_arrow = find_arrow(row, col)

                # 如果找到了箭头
                if clicked_arrow is not None:
                    print("点击到了箭头：", clicked_arrow)

                # 如果没有找到箭头
                else:
                    print("这个格子没有箭头")

    # 清空屏幕，设置白色背景
    screen.fill((255, 255, 255))

    # 绘制棋盘
    for row in range(ROWS):
        for col in range(COLS):

            # 计算每个格子的左上角坐标
            x = BOARD_X + col * CELL_SIZE
            y = BOARD_Y + row * CELL_SIZE

            pygame.draw.rect(
                screen,
                (0, 0, 0),
                (x, y, CELL_SIZE, CELL_SIZE),
                1
            )

    # 绘制所有箭头
    for arrow in arrows:
        draw_arrow(
            screen,
            arrow["row"],
            arrow["col"],
            arrow["direction"]
        )

    # 刷新屏幕
    pygame.display.flip()

# 退出 pygame
pygame.quit()