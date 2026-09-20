# 导入 pygame 库，后续才可以使用 pygame 中的功能
import pygame

# 初始化 pygame，让 pygame 把需要使用的各个模块初始化好
pygame.init()

# 创建一个字号为 60 的字体对象，并保存到变量 font 中
# None 表示不指定字体文件，使用 pygame 默认字体
# 60 表示字体大小
font = pygame.font.Font(None, 60)

"""
pygame.display 表示 pygame 中负责显示窗口的模块
set_mode 表示创建一个窗口
(800, 600) 表示窗口宽 800 像素，高 600 像素
screen 用来保存创建出来的窗口对象
"""
screen = pygame.display.set_mode((800, 600))

"""
ROWS = 5        → 棋盘共 5 行
COLS = 5        → 棋盘共 5 列
CELL_SIZE = 80  → 每个格子大小为 80×80 像素
BOARD_X = 200   → 棋盘左上角的 x 坐标
BOARD_Y = 100   → 棋盘左上角的 y 坐标
"""
ROWS = 5
COLS = 5
CELL_SIZE = 80

BOARD_X = 200
BOARD_Y = 100

# running 用来控制游戏是否继续运行
running = True

# 游戏主循环
while running:

    # pygame.event.get() 获取当前等待处理的所有事件
    # for 会把这些事件一个一个取出来，当前事件保存在 event 中
    for event in pygame.event.get():

        # 如果当前事件是关闭窗口
        if event.type == pygame.QUIT:
            running = False

    # 把整个窗口填充为白色
    screen.fill((255, 255, 255))

    """
    下面使用双重 for 循环绘制 5×5 棋盘。

    如果 ROWS = 5：
    range(ROWS) 会产生 0、1、2、3、4。

    外层循环负责行，
    内层循环负责列。
    """

    for row in range(ROWS):
        for col in range(COLS):

            # 根据当前行和列计算格子的左上角坐标
            x = BOARD_X + col * CELL_SIZE
            y = BOARD_Y + row * CELL_SIZE

            """
            pygame.draw.rect() 用来绘制矩形。

            参数分别是：
            1. screen：画在哪个窗口上
            2. (0, 0, 0)：矩形颜色为黑色
            3. (x, y, CELL_SIZE, CELL_SIZE)：
               矩形左上角坐标和宽高
            4. 1：只绘制宽度为 1 像素的边框

            如果最后的 width 参数写成 0 或省略，
            矩形内部会被填满。
            """
            pygame.draw.rect(
                screen,
                (0, 0, 0),
                (x, y, CELL_SIZE, CELL_SIZE),
                1
            )

    """
    使用 font.render() 把字符串 "→" 制作成一个可以绘制的图像对象。

    三个参数分别是：
    1. "→"：需要显示的文字
    2. True：开启抗锯齿，使边缘更平滑
    3. (0, 0, 0)：文字颜色为黑色
    """
    arrow_text = font.render("→", True, (0, 0, 0))

    # 把箭头放在 row=2、col=2 的格子中
    # 因为 Python 从 0 开始计数，所以实际上是第 3 行第 3 列
    row = 2
    col = 2

    # 计算这个格子的左上角坐标
    x = BOARD_X + col * CELL_SIZE
    y = BOARD_Y + row * CELL_SIZE

    """
    get_rect() 给箭头文字生成一个矩形区域。

    center 表示设置这个矩形的中心位置。

    CELL_SIZE // 2：
    80 // 2 = 40

    所以：
    x + 40
    y + 40

    正好就是当前格子的中心点。
    """
    arrow_rect = arrow_text.get_rect(
        center=(
            x + CELL_SIZE // 2,
            y + CELL_SIZE // 2
        )
    )

    # 把箭头图像绘制到 screen 上
    screen.blit(arrow_text, arrow_rect)

    # 把当前这一帧真正刷新显示到窗口
    pygame.display.flip()

# 游戏循环结束后关闭 pygame
pygame.quit()