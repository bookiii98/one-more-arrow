import pygame


# =========================================================
# 1. pygame 初始化
# =========================================================

pygame.init()

screen = pygame.display.set_mode(
    (800, 700),
    pygame.RESIZABLE
)

pygame.display.set_caption("One More Arrow")

clock = pygame.time.Clock()


# =========================================================
# 2. 字体
# =========================================================

title_font = pygame.font.Font(None, 80)
big_font = pygame.font.Font(None, 60)
info_font = pygame.font.Font(None, 32)
button_font = pygame.font.Font(None, 34)


# =========================================================
# 3. 棋盘参数
# =========================================================

ROWS = 5
COLS = 5

CELL_SIZE = 80

BOARD_X = 200
BOARD_Y = 100

MAX_CELL_SIZE = 110


# =========================================================
# 4. 游戏基础参数
# =========================================================

MAX_MISTAKES = 3

mistakes_left = MAX_MISTAKES


# =========================================================
# 5. 三个关卡
# =========================================================

LEVELS = [

    # -----------------------------------------------------
    # Level 1
    # 8 个箭头
    # -----------------------------------------------------

    [
        {"row": 0, "col": 0, "direction": "right"},
        {"row": 0, "col": 3, "direction": "down"},

        {"row": 1, "col": 1, "direction": "right"},
        {"row": 1, "col": 4, "direction": "down"},

        {"row": 3, "col": 1, "direction": "up"},
        {"row": 3, "col": 3, "direction": "left"},

        {"row": 4, "col": 2, "direction": "up"},
        {"row": 4, "col": 4, "direction": "left"}
    ],


    # -----------------------------------------------------
    # Level 2
    # 12 个箭头
    # -----------------------------------------------------

    [
        {"row": 4, "col": 4, "direction": "right"},
        {"row": 2, "col": 4, "direction": "right"},

        {"row": 0, "col": 3, "direction": "up"},
        {"row": 0, "col": 0, "direction": "down"},
        {"row": 0, "col": 2, "direction": "down"},

        {"row": 3, "col": 3, "direction": "left"},

        {"row": 0, "col": 1, "direction": "right"},

        {"row": 4, "col": 0, "direction": "left"},
        {"row": 4, "col": 2, "direction": "right"},

        {"row": 2, "col": 1, "direction": "right"},

        {"row": 3, "col": 1, "direction": "down"},

        {"row": 4, "col": 1, "direction": "left"}
    ],


    # -----------------------------------------------------
    # Level 3
    # 16 个箭头
    # -----------------------------------------------------

    [
        {"row": 4, "col": 4, "direction": "right"},
        {"row": 1, "col": 3, "direction": "right"},

        {"row": 3, "col": 3, "direction": "left"},

        {"row": 0, "col": 1, "direction": "up"},
        {"row": 2, "col": 3, "direction": "up"},
        {"row": 1, "col": 4, "direction": "up"},

        {"row": 4, "col": 1, "direction": "down"},
        {"row": 4, "col": 3, "direction": "left"},

        {"row": 0, "col": 2, "direction": "up"},
        {"row": 0, "col": 3, "direction": "right"},

        {"row": 4, "col": 2, "direction": "up"},

        {"row": 0, "col": 0, "direction": "down"},
        {"row": 0, "col": 4, "direction": "up"},

        {"row": 1, "col": 1, "direction": "up"},
        {"row": 1, "col": 0, "direction": "down"},

        {"row": 2, "col": 4, "direction": "right"}
    ]
]


# =========================================================
# 6. 当前关卡
# =========================================================

# Python 从 0 开始计数
# 0 = 第一关
# 1 = 第二关
# 2 = 第三关

current_level = 0

# 当前关卡真正使用的箭头
arrows = []


# =========================================================
# 7. 游戏状态
# =========================================================

# start
# playing
# game_over
# level_complete
# all_clear

game_state = "start"


# =========================================================
# 8. 动画数据
# =========================================================

flying_arrow = None

collision_arrow = None
collision_blocker = None

collision_frame = 0

COLLISION_TOTAL_FRAMES = 40

collision_target_distance = 0


# =========================================================
# 9. 自适应布局
# =========================================================

def update_layout():

    global CELL_SIZE
    global BOARD_X
    global BOARD_Y

    window_width, window_height = screen.get_size()

    # 给顶部信息栏和底部留一些空间
    available_width = window_width - 120
    available_height = window_height - 220

    cell_by_width = available_width // COLS
    cell_by_height = available_height // ROWS

    CELL_SIZE = min(
        cell_by_width,
        cell_by_height,
        MAX_CELL_SIZE
    )

    # 防止窗口特别小时格子异常
    CELL_SIZE = max(
        CELL_SIZE,
        25
    )

    board_width = (
        COLS * CELL_SIZE
    )

    board_height = (
        ROWS * CELL_SIZE
    )

    # 水平居中
    BOARD_X = (
        window_width - board_width
    ) // 2

    # 垂直居中，并稍微向下
    BOARD_Y = (
        window_height - board_height
    ) // 2 + 20


# =========================================================
# 10. 加载指定关卡
# =========================================================

def load_level(level_index):

    global arrows
    global mistakes_left
    global game_state

    global flying_arrow

    global collision_arrow
    global collision_blocker
    global collision_frame
    global collision_target_distance

    # -----------------------------------------------------
    # 复制当前关卡箭头
    # -----------------------------------------------------

    arrows = [

        arrow.copy()

        for arrow in LEVELS[level_index]
    ]

    # -----------------------------------------------------
    # 恢复失误次数
    # -----------------------------------------------------

    mistakes_left = MAX_MISTAKES


    # -----------------------------------------------------
    # 清除动画
    # -----------------------------------------------------

    flying_arrow = None

    collision_arrow = None
    collision_blocker = None

    collision_frame = 0
    collision_target_distance = 0


    # -----------------------------------------------------
    # 回到游戏状态
    # -----------------------------------------------------

    game_state = "playing"

    print(
        "进入第",
        level_index + 1,
        "关"
    )


# =========================================================
# 11. 开始新游戏
# =========================================================

def start_new_game():

    global current_level

    # 从第一关开始
    current_level = 0

    load_level(
        current_level
    )


# =========================================================
# 12. 重置当前关卡
# =========================================================

def restart_current_level():

    load_level(
        current_level
    )

    print(
        "重新开始当前关卡"
    )


# =========================================================
# 13. 进入下一关
# =========================================================

def go_to_next_level():

    global current_level

    # 当前还不是最后一关
    if (
        current_level
        < len(LEVELS) - 1
    ):

        current_level += 1

        load_level(
            current_level
        )


# =========================================================
# 14. 绘制按钮
# =========================================================

def draw_button(
    rect,
    text
):

    mouse_x, mouse_y = (
        pygame.mouse.get_pos()
    )

    # 鼠标放到按钮上时改变颜色
    if rect.collidepoint(
        mouse_x,
        mouse_y
    ):

        background_color = (
            210,
            215,
            225
        )

    else:

        background_color = (
            235,
            238,
            245
        )

    # 按钮背景
    pygame.draw.rect(
        screen,
        background_color,
        rect,
        border_radius=10
    )

    # 按钮边框
    pygame.draw.rect(
        screen,
        (70, 75, 85),
        rect,
        2,
        border_radius=10
    )

    # 按钮文字
    text_surface = (
        button_font.render(
            text,
            True,
            (30, 30, 35)
        )
    )

    text_rect = (
        text_surface.get_rect(
            center=rect.center
        )
    )

    screen.blit(
        text_surface,
        text_rect
    )


# =========================================================
# 15. 绘制箭头
# =========================================================

def draw_arrow(
    screen,
    row,
    col,
    direction,
    offset_x=0,
    offset_y=0,
    color=(30, 30, 30)
):

    center_x = (
        BOARD_X
        + col * CELL_SIZE
        + CELL_SIZE // 2
        + offset_x
    )

    center_y = (
        BOARD_Y
        + row * CELL_SIZE
        + CELL_SIZE // 2
        + offset_y
    )


    # 箭头尺寸随格子大小变化
    body_length = int(
        CELL_SIZE * 0.30
    )

    head_size = int(
        CELL_SIZE * 0.12
    )

    line_width = max(
        2,
        int(CELL_SIZE * 0.05)
    )


    # -----------------------------------------------------
    # 向右
    # -----------------------------------------------------

    if direction == "right":

        start = (
            center_x - body_length,
            center_y
        )

        end = (
            center_x + body_length,
            center_y
        )

        pygame.draw.line(
            screen,
            color,
            start,
            end,
            line_width
        )

        pygame.draw.line(
            screen,
            color,
            end,
            (
                end[0] - head_size,
                end[1] - head_size
            ),
            line_width
        )

        pygame.draw.line(
            screen,
            color,
            end,
            (
                end[0] - head_size,
                end[1] + head_size
            ),
            line_width
        )


    # -----------------------------------------------------
    # 向左
    # -----------------------------------------------------

    elif direction == "left":

        start = (
            center_x + body_length,
            center_y
        )

        end = (
            center_x - body_length,
            center_y
        )

        pygame.draw.line(
            screen,
            color,
            start,
            end,
            line_width
        )

        pygame.draw.line(
            screen,
            color,
            end,
            (
                end[0] + head_size,
                end[1] - head_size
            ),
            line_width
        )

        pygame.draw.line(
            screen,
            color,
            end,
            (
                end[0] + head_size,
                end[1] + head_size
            ),
            line_width
        )


    # -----------------------------------------------------
    # 向上
    # -----------------------------------------------------

    elif direction == "up":

        start = (
            center_x,
            center_y + body_length
        )

        end = (
            center_x,
            center_y - body_length
        )

        pygame.draw.line(
            screen,
            color,
            start,
            end,
            line_width
        )

        pygame.draw.line(
            screen,
            color,
            end,
            (
                end[0] - head_size,
                end[1] + head_size
            ),
            line_width
        )

        pygame.draw.line(
            screen,
            color,
            end,
            (
                end[0] + head_size,
                end[1] + head_size
            ),
            line_width
        )


    # -----------------------------------------------------
    # 向下
    # -----------------------------------------------------

    elif direction == "down":

        start = (
            center_x,
            center_y - body_length
        )

        end = (
            center_x,
            center_y + body_length
        )

        pygame.draw.line(
            screen,
            color,
            start,
            end,
            line_width
        )

        pygame.draw.line(
            screen,
            color,
            end,
            (
                end[0] - head_size,
                end[1] - head_size
            ),
            line_width
        )

        pygame.draw.line(
            screen,
            color,
            end,
            (
                end[0] + head_size,
                end[1] - head_size
            ),
            line_width
        )


# =========================================================
# 16. 根据格子寻找箭头
# =========================================================

def find_arrow(
    row,
    col
):

    for arrow in arrows:

        if (
            arrow["row"] == row
            and arrow["col"] == col
        ):

            return arrow

    return None


# =========================================================
# 17. 寻找最近阻挡箭头
# =========================================================

def find_blocker(
    arrow
):

    row = arrow["row"]
    col = arrow["col"]

    direction = (
        arrow["direction"]
    )

    nearest_blocker = None
    nearest_distance = None


    for other in arrows:

        # 不能自己挡自己
        if other is arrow:
            continue


        # -------------------------------------------------
        # 向右
        # -------------------------------------------------

        if direction == "right":

            if (
                other["row"] == row
                and other["col"] > col
            ):

                distance = (
                    other["col"] - col
                )

                if (
                    nearest_distance is None
                    or distance < nearest_distance
                ):

                    nearest_distance = (
                        distance
                    )

                    nearest_blocker = (
                        other
                    )


        # -------------------------------------------------
        # 向左
        # -------------------------------------------------

        elif direction == "left":

            if (
                other["row"] == row
                and other["col"] < col
            ):

                distance = (
                    col - other["col"]
                )

                if (
                    nearest_distance is None
                    or distance < nearest_distance
                ):

                    nearest_distance = (
                        distance
                    )

                    nearest_blocker = (
                        other
                    )


        # -------------------------------------------------
        # 向下
        # -------------------------------------------------

        elif direction == "down":

            if (
                other["col"] == col
                and other["row"] > row
            ):

                distance = (
                    other["row"] - row
                )

                if (
                    nearest_distance is None
                    or distance < nearest_distance
                ):

                    nearest_distance = (
                        distance
                    )

                    nearest_blocker = (
                        other
                    )


        # -------------------------------------------------
        # 向上
        # -------------------------------------------------

        elif direction == "up":

            if (
                other["col"] == col
                and other["row"] < row
            ):

                distance = (
                    row - other["row"]
                )

                if (
                    nearest_distance is None
                    or distance < nearest_distance
                ):

                    nearest_distance = (
                        distance
                    )

                    nearest_blocker = (
                        other
                    )


    return nearest_blocker


# =========================================================
# 18. 初始化箭头数据
# =========================================================

arrows = [

    arrow.copy()

    for arrow in LEVELS[0]
]


# =========================================================
# 19. 主循环
# =========================================================

running = True


while running:

    update_layout()

    window_width, window_height = (
        screen.get_size()
    )


    # =====================================================
    # 20. 按钮的位置
    # =====================================================

    start_button = pygame.Rect(
        window_width // 2 - 100,
        window_height // 2 + 60,
        200,
        60
    )


    restart_button = pygame.Rect(
        window_width - 150,
        20,
        120,
        45
    )


    modal_button = pygame.Rect(
        window_width // 2 - 100,
        window_height // 2 + 70,
        200,
        55
    )


    # =====================================================
    # 21. 事件处理
    # =====================================================

    for event in pygame.event.get():

        # -------------------------------------------------
        # 关闭窗口
        # -------------------------------------------------

        if event.type == pygame.QUIT:

            running = False


        # -------------------------------------------------
        # 调整窗口大小
        # -------------------------------------------------

        if event.type == pygame.VIDEORESIZE:

            screen = pygame.display.set_mode(
                (
                    event.w,
                    event.h
                ),
                pygame.RESIZABLE
            )

            update_layout()


        # -------------------------------------------------
        # 鼠标点击
        # -------------------------------------------------

        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = event.pos


            # =============================================
            # 开始界面
            # =============================================

            if game_state == "start":

                if start_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    start_new_game()

                continue


            # =============================================
            # 游戏失败
            # =============================================

            if game_state == "game_over":

                if modal_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    restart_current_level()

                continue


            # =============================================
            # 当前关卡完成
            # =============================================

            if game_state == "level_complete":

                if modal_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    go_to_next_level()

                continue


            # =============================================
            # 全部关卡完成
            # =============================================

            if game_state == "all_clear":

                if modal_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    start_new_game()

                continue


            # =============================================
            # 正常游戏
            # =============================================

            if game_state == "playing":


                # -----------------------------------------
                # Restart
                # -----------------------------------------

                if restart_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    restart_current_level()

                    continue


                # -----------------------------------------
                # 动画过程中禁止点击
                # -----------------------------------------

                if (
                    flying_arrow is not None
                    or collision_arrow is not None
                ):

                    continue


                # -----------------------------------------
                # 判断是否点击棋盘
                # -----------------------------------------

                if (
                    BOARD_X
                    <= mouse_x
                    < BOARD_X + COLS * CELL_SIZE

                    and

                    BOARD_Y
                    <= mouse_y
                    < BOARD_Y + ROWS * CELL_SIZE
                ):

                    col = (
                        mouse_x - BOARD_X
                    ) // CELL_SIZE

                    row = (
                        mouse_y - BOARD_Y
                    ) // CELL_SIZE


                    clicked_arrow = find_arrow(
                        row,
                        col
                    )


                    # -------------------------------------
                    # 点击到了箭头
                    # -------------------------------------

                    if clicked_arrow is not None:

                        print(
                            "点击到了箭头：",
                            clicked_arrow
                        )


                        blocker = find_blocker(
                            clicked_arrow
                        )


                        # =================================
                        # 被挡住
                        # =================================

                        if blocker is not None:

                            print(
                                "这个箭头被挡住了"
                            )

                            print(
                                "阻挡它的箭头：",
                                blocker
                            )


                            # -----------------------------
                            # 扣除失误次数
                            # -----------------------------

                            if mistakes_left > 0:

                                mistakes_left -= 1


                            print(
                                "剩余失误次数：",
                                mistakes_left
                            )


                            # -----------------------------
                            # 开始碰撞动画
                            # -----------------------------

                            collision_arrow = (
                                clicked_arrow
                            )

                            collision_blocker = (
                                blocker
                            )

                            collision_frame = 0


                            direction = (
                                clicked_arrow[
                                    "direction"
                                ]
                            )


                            # -----------------------------
                            # 算箭头与障碍之间有多少格
                            # -----------------------------

                            if direction == "right":

                                cells_between = (
                                    blocker["col"]
                                    - clicked_arrow["col"]
                                )


                            elif direction == "left":

                                cells_between = (
                                    clicked_arrow["col"]
                                    - blocker["col"]
                                )


                            elif direction == "down":

                                cells_between = (
                                    blocker["row"]
                                    - clicked_arrow["row"]
                                )


                            else:

                                cells_between = (
                                    clicked_arrow["row"]
                                    - blocker["row"]
                                )


                            # -----------------------------
                            # 防止两个箭头完全重叠
                            # -----------------------------

                            safe_distance = int(
                                CELL_SIZE * 0.62
                            )


                            collision_target_distance = (
                                cells_between
                                * CELL_SIZE
                                - safe_distance
                            )


                            collision_target_distance = max(
                                int(
                                    CELL_SIZE * 0.15
                                ),
                                collision_target_distance
                            )


                            # -----------------------------
                            # 游戏失败
                            # -----------------------------

                            if mistakes_left == 0:

                                game_state = (
                                    "game_over"
                                )


                        # =================================
                        # 没有被阻挡
                        # =================================

                        else:

                            print(
                                "这个箭头可以飞出去"
                            )


                            flying_arrow = (
                                clicked_arrow.copy()
                            )


                            flying_arrow[
                                "offset_x"
                            ] = 0


                            flying_arrow[
                                "offset_y"
                            ] = 0


                            # 从棋盘逻辑数据中删除
                            arrows.remove(
                                clicked_arrow
                            )


    # =====================================================
    # 22. 飞出动画
    # =====================================================

    if flying_arrow is not None:

        direction = (
            flying_arrow["direction"]
        )


        fly_speed = max(
            4,
            int(CELL_SIZE * 0.10)
        )


        if direction == "right":

            flying_arrow[
                "offset_x"
            ] += fly_speed


        elif direction == "left":

            flying_arrow[
                "offset_x"
            ] -= fly_speed


        elif direction == "up":

            flying_arrow[
                "offset_y"
            ] -= fly_speed


        elif direction == "down":

            flying_arrow[
                "offset_y"
            ] += fly_speed


        current_x = (
            BOARD_X
            + flying_arrow["col"]
            * CELL_SIZE
            + CELL_SIZE // 2
            + flying_arrow["offset_x"]
        )


        current_y = (
            BOARD_Y
            + flying_arrow["row"]
            * CELL_SIZE
            + CELL_SIZE // 2
            + flying_arrow["offset_y"]
        )


        # 飞出棋盘后结束动画
        if (
            current_x < BOARD_X
            or current_x > BOARD_X
            + COLS * CELL_SIZE

            or

            current_y < BOARD_Y
            or current_y > BOARD_Y
            + ROWS * CELL_SIZE
        ):

            flying_arrow = None


    # =====================================================
    # 23. 碰撞动画
    # =====================================================

    collision_offset_x = 0
    collision_offset_y = 0


    if collision_arrow is not None:

        collision_frame += 1


        # -------------------------------------------------
        # 前半段：向阻挡箭头移动
        # -------------------------------------------------

        if (
            collision_frame
            <= COLLISION_TOTAL_FRAMES // 2
        ):

            progress = (
                collision_frame
                /
                (
                    COLLISION_TOTAL_FRAMES
                    // 2
                )
            )


        # -------------------------------------------------
        # 后半段：返回
        # -------------------------------------------------

        else:

            progress = (
                COLLISION_TOTAL_FRAMES
                - collision_frame
            ) / (
                COLLISION_TOTAL_FRAMES
                // 2
            )


        distance = int(
            collision_target_distance
            * progress
        )


        direction = (
            collision_arrow["direction"]
        )


        if direction == "right":

            collision_offset_x = (
                distance
            )


        elif direction == "left":

            collision_offset_x = (
                -distance
            )


        elif direction == "up":

            collision_offset_y = (
                -distance
            )


        elif direction == "down":

            collision_offset_y = (
                distance
            )


        # -------------------------------------------------
        # 碰撞动画结束
        # -------------------------------------------------

        if (
            collision_frame
            >= COLLISION_TOTAL_FRAMES
        ):

            collision_arrow = None
            collision_blocker = None

            collision_frame = 0


    # =====================================================
    # 24. 判断当前关卡是否完成
    # =====================================================

    if (
        game_state == "playing"
        and len(arrows) == 0
        and flying_arrow is None
    ):

        # -------------------------------------------------
        # 还有下一关
        # -------------------------------------------------

        if (
            current_level
            < len(LEVELS) - 1
        ):

            game_state = (
                "level_complete"
            )

            print(
                "第",
                current_level + 1,
                "关通关"
            )


        # -------------------------------------------------
        # 第三关也完成了
        # -------------------------------------------------

        else:

            game_state = (
                "all_clear"
            )

            print(
                "所有关卡全部完成"
            )


    # =====================================================
    # 25. 绘制背景
    # =====================================================

    screen.fill(
        (245, 247, 250)
    )


    # =====================================================
    # 26. 开始界面
    # =====================================================

    if game_state == "start":

        title = title_font.render(
            "One More Arrow",
            True,
            (30, 30, 35)
        )


        title_rect = title.get_rect(
            center=(
                window_width // 2,
                window_height // 2 - 80
            )
        )


        screen.blit(
            title,
            title_rect
        )


        tip = info_font.render(
            "Clear every arrow without hitting blockers",
            True,
            (90, 95, 105)
        )


        tip_rect = tip.get_rect(
            center=(
                window_width // 2,
                window_height // 2
            )
        )


        screen.blit(
            tip,
            tip_rect
        )


        draw_button(
            start_button,
            "Start Game"
        )


    # =====================================================
    # 27. 游戏画面
    # =====================================================

    else:

        # -------------------------------------------------
        # 当前关卡
        # -------------------------------------------------

        level_text = info_font.render(
            "Level "
            + str(current_level + 1)
            + " / "
            + str(len(LEVELS)),
            True,
            (30, 30, 35)
        )


        screen.blit(
            level_text,
            (20, 20)
        )


        # -------------------------------------------------
        # 失误次数
        # -------------------------------------------------

        mistakes_text = info_font.render(
            "Mistakes: "
            + str(mistakes_left),
            True,
            (30, 30, 35)
        )


        screen.blit(
            mistakes_text,
            (20, 55)
        )


        # -------------------------------------------------
        # 剩余箭头
        # -------------------------------------------------

        remaining_text = info_font.render(
            "Remaining: "
            + str(len(arrows)),
            True,
            (30, 30, 35)
        )


        screen.blit(
            remaining_text,
            (20, 90)
        )


        # -------------------------------------------------
        # Restart 按钮
        # -------------------------------------------------

        draw_button(
            restart_button,
            "Restart"
        )


        # =================================================
        # 棋盘
        # =================================================

        for row in range(ROWS):

            for col in range(COLS):

                x = (
                    BOARD_X
                    + col * CELL_SIZE
                )

                y = (
                    BOARD_Y
                    + row * CELL_SIZE
                )


                # 单元格背景
                pygame.draw.rect(
                    screen,
                    (255, 255, 255),
                    (
                        x,
                        y,
                        CELL_SIZE,
                        CELL_SIZE
                    )
                )


                # 单元格边框
                pygame.draw.rect(
                    screen,
                    (180, 185, 195),
                    (
                        x,
                        y,
                        CELL_SIZE,
                        CELL_SIZE
                    ),
                    1
                )


        # =================================================
        # 棋盘上的箭头
        # =================================================

        for arrow in arrows:

            # 当前正在发生碰撞
            if arrow is collision_arrow:

                draw_arrow(
                    screen,
                    arrow["row"],
                    arrow["col"],
                    arrow["direction"],
                    collision_offset_x,
                    collision_offset_y,
                    (220, 40, 40)
                )


            else:

                draw_arrow(
                    screen,
                    arrow["row"],
                    arrow["col"],
                    arrow["direction"]
                )


        # =================================================
        # 正在飞出去的箭头
        # =================================================

        if flying_arrow is not None:

            draw_arrow(
                screen,
                flying_arrow["row"],
                flying_arrow["col"],
                flying_arrow["direction"],
                flying_arrow["offset_x"],
                flying_arrow["offset_y"]
            )


        # =================================================
        # 28. Game Over 弹窗
        # =================================================

        if game_state == "game_over":

            overlay = pygame.Surface(
                (
                    window_width,
                    window_height
                ),
                pygame.SRCALPHA
            )


            overlay.fill(
                (
                    0,
                    0,
                    0,
                    110
                )
            )


            screen.blit(
                overlay,
                (0, 0)
            )


            modal_width = min(
                430,
                window_width - 40
            )


            modal_height = 250


            modal_rect = pygame.Rect(
                window_width // 2
                - modal_width // 2,

                window_height // 2
                - modal_height // 2,

                modal_width,
                modal_height
            )


            pygame.draw.rect(
                screen,
                (255, 255, 255),
                modal_rect,
                border_radius=18
            )


            text = big_font.render(
                "Game Over",
                True,
                (210, 45, 45)
            )


            text_rect = text.get_rect(
                center=(
                    window_width // 2,
                    window_height // 2 - 45
                )
            )


            screen.blit(
                text,
                text_rect
            )


            draw_button(
                modal_button,
                "Restart"
            )


        # =================================================
        # 29. Level Complete 弹窗
        # =================================================

        elif game_state == "level_complete":

            overlay = pygame.Surface(
                (
                    window_width,
                    window_height
                ),
                pygame.SRCALPHA
            )


            overlay.fill(
                (
                    0,
                    0,
                    0,
                    110
                )
            )


            screen.blit(
                overlay,
                (0, 0)
            )


            modal_width = min(
                470,
                window_width - 40
            )


            modal_height = 250


            modal_rect = pygame.Rect(
                window_width // 2
                - modal_width // 2,

                window_height // 2
                - modal_height // 2,

                modal_width,
                modal_height
            )


            pygame.draw.rect(
                screen,
                (255, 255, 255),
                modal_rect,
                border_radius=18
            )


            text = big_font.render(
                "Level Complete!",
                True,
                (35, 160, 85)
            )


            text_rect = text.get_rect(
                center=(
                    window_width // 2,
                    window_height // 2 - 45
                )
            )


            screen.blit(
                text,
                text_rect
            )


            draw_button(
                modal_button,
                "Next Level"
            )


        # =================================================
        # 30. 全部关卡完成
        # =================================================

        elif game_state == "all_clear":

            overlay = pygame.Surface(
                (
                    window_width,
                    window_height
                ),
                pygame.SRCALPHA
            )


            overlay.fill(
                (
                    0,
                    0,
                    0,
                    115
                )
            )


            screen.blit(
                overlay,
                (0, 0)
            )


            modal_width = min(
                500,
                window_width - 40
            )


            modal_height = 270


            modal_rect = pygame.Rect(
                window_width // 2
                - modal_width // 2,

                window_height // 2
                - modal_height // 2,

                modal_width,
                modal_height
            )


            pygame.draw.rect(
                screen,
                (255, 255, 255),
                modal_rect,
                border_radius=18
            )


            title = big_font.render(
                "Congratulations!",
                True,
                (35, 150, 85)
            )


            title_rect = (
                title.get_rect(
                    center=(
                        window_width // 2,
                        window_height // 2 - 65
                    )
                )
            )


            screen.blit(
                title,
                title_rect
            )


            subtitle = info_font.render(
                "All Levels Clear!",
                True,
                (70, 75, 85)
            )


            subtitle_rect = (
                subtitle.get_rect(
                    center=(
                        window_width // 2,
                        window_height // 2
                    )
                )
            )


            screen.blit(
                subtitle,
                subtitle_rect
            )


            draw_button(
                modal_button,
                "Play Again"
            )


    # =====================================================
    # 31. 更新屏幕
    # =====================================================

    pygame.display.flip()

    clock.tick(60)


# =========================================================
# 32. 退出 pygame
# =========================================================

pygame.quit()