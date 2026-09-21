import pygame


# =========================================================
# 1. pygame 初始化
# =========================================================

pygame.init()

screen = pygame.display.set_mode(
    (900, 760),
    pygame.RESIZABLE
)

pygame.display.set_caption("One More Arrow")

clock = pygame.time.Clock()


# =========================================================
# 2. 字体
# =========================================================

title_font = pygame.font.Font(None, 86)
big_font = pygame.font.Font(None, 62)
info_font = pygame.font.Font(None, 30)
small_font = pygame.font.Font(None, 24)
button_font = pygame.font.Font(None, 34)


# =========================================================
# 3. 颜色
# =========================================================

BACKGROUND = (241, 244, 249)

CARD_BG = (255, 255, 255)

TEXT_MAIN = (35, 40, 50)
TEXT_SECONDARY = (100, 108, 120)

GRID_COLOR = (214, 219, 228)

BUTTON_BG = (245, 247, 252)
BUTTON_HOVER = (226, 232, 243)
BUTTON_BORDER = (125, 135, 150)

RED = (220, 65, 65)
GREEN = (50, 165, 105)
BLUE = (70, 120, 220)
ORANGE = (235, 145, 60)
PURPLE = (150, 95, 205)
TEAL = (45, 165, 170)

OVERLAY_COLOR = (20, 25, 35, 120)


# =========================================================
# 4. 棋盘参数
# =========================================================

ROWS = 5
COLS = 5

CELL_SIZE = 80

BOARD_X = 200
BOARD_Y = 160

MAX_CELL_SIZE = 105


# =========================================================
# 5. 游戏参数
# =========================================================

MAX_MISTAKES = 3

mistakes_left = MAX_MISTAKES

current_level = 0

game_state = "start"


# =========================================================
# 6. 三个关卡
# =========================================================

LEVELS = [

    # Level 1
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

    # Level 2
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

    # Level 3
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


arrows = []


# =========================================================
# 7. 动画数据
# =========================================================

flying_arrow = None

collision_arrow = None
collision_blocker = None

collision_frame = 0

COLLISION_TOTAL_FRAMES = 40

collision_target_distance = 0


# =========================================================
# 8. 动态布局
# =========================================================

def update_layout():

    global CELL_SIZE
    global BOARD_X
    global BOARD_Y

    window_width, window_height = screen.get_size()

    available_width = window_width - 160
    available_height = window_height - 280

    cell_by_width = available_width // COLS
    cell_by_height = available_height // ROWS

    CELL_SIZE = min(
        cell_by_width,
        cell_by_height,
        MAX_CELL_SIZE
    )

    CELL_SIZE = max(
        CELL_SIZE,
        28
    )

    board_width = COLS * CELL_SIZE
    board_height = ROWS * CELL_SIZE

    BOARD_X = (
        window_width - board_width
    ) // 2

    BOARD_Y = (
        window_height - board_height
    ) // 2 + 45


# =========================================================
# 9. 加载关卡
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

    arrows = [
        arrow.copy()
        for arrow in LEVELS[level_index]
    ]

    mistakes_left = MAX_MISTAKES

    flying_arrow = None

    collision_arrow = None
    collision_blocker = None

    collision_frame = 0
    collision_target_distance = 0

    game_state = "playing"

    print(
        "进入第",
        level_index + 1,
        "关"
    )


def start_new_game():

    global current_level

    current_level = 0

    load_level(
        current_level
    )


def restart_current_level():

    load_level(
        current_level
    )

    print(
        "重新开始当前关卡"
    )


def go_to_next_level():

    global current_level

    if (
        current_level
        < len(LEVELS) - 1
    ):

        current_level += 1

        load_level(
            current_level
        )


# =========================================================
# 10. UI 辅助函数
# =========================================================

def draw_shadow_rect(
    rect,
    radius=16,
    shadow_offset=6
):

    shadow_rect = rect.copy()

    shadow_rect.x += shadow_offset
    shadow_rect.y += shadow_offset

    pygame.draw.rect(
        screen,
        (215, 220, 230),
        shadow_rect,
        border_radius=radius
    )


def draw_button(
    rect,
    text,
    accent=False
):

    mouse_x, mouse_y = (
        pygame.mouse.get_pos()
    )

    hovered = rect.collidepoint(
        mouse_x,
        mouse_y
    )

    if accent:

        if hovered:
            background_color = (
                62,
                112,
                210
            )
        else:
            background_color = (
                72,
                125,
                225
            )

        text_color = (
            255,
            255,
            255
        )

        border_color = (
            72,
            125,
            225
        )

    else:

        if hovered:
            background_color = (
                228,
                233,
                244
            )
        else:
            background_color = (
                245,
                247,
                252
            )

        text_color = (
            45,
            50,
            60
        )

        border_color = (
            150,
            160,
            175
        )

    pygame.draw.rect(
        screen,
        background_color,
        rect,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        border_color,
        rect,
        2,
        border_radius=12
    )

    text_surface = (
        button_font.render(
            text,
            True,
            text_color
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


def draw_info_card(
    rect,
    title,
    value,
    accent_color
):

    draw_shadow_rect(
        rect,
        radius=14,
        shadow_offset=4
    )

    pygame.draw.rect(
        screen,
        CARD_BG,
        rect,
        border_radius=14
    )

    accent_rect = pygame.Rect(
        rect.x,
        rect.y,
        6,
        rect.height
    )

    pygame.draw.rect(
        screen,
        accent_color,
        accent_rect,
        border_radius=6
    )

    title_surface = (
        small_font.render(
            title,
            True,
            TEXT_SECONDARY
        )
    )

    value_surface = (
        info_font.render(
            value,
            True,
            TEXT_MAIN
        )
    )

    screen.blit(
        title_surface,
        (
            rect.x + 20,
            rect.y + 12
        )
    )

    screen.blit(
        value_surface,
        (
            rect.x + 20,
            rect.y + 34
        )
    )


# =========================================================
# 11. 箭头颜色
# =========================================================

def get_arrow_color(direction):

    if direction == "right":
        return BLUE

    if direction == "left":
        return PURPLE

    if direction == "up":
        return TEAL

    if direction == "down":
        return ORANGE

    return TEXT_MAIN


# =========================================================
# 12. 绘制箭头
# =========================================================

def draw_arrow(
    screen,
    row,
    col,
    direction,
    offset_x=0,
    offset_y=0,
    color=None
):

    if color is None:
        color = get_arrow_color(
            direction
        )

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

    body_length = int(
        CELL_SIZE * 0.28
    )

    head_size = int(
        CELL_SIZE * 0.13
    )

    line_width = max(
        3,
        int(CELL_SIZE * 0.055)
    )


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
# 13. 查找箭头
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
# 14. 查找最近阻挡箭头
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

        if other is arrow:
            continue


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

                    nearest_distance = distance
                    nearest_blocker = other


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

                    nearest_distance = distance
                    nearest_blocker = other


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

                    nearest_distance = distance
                    nearest_blocker = other


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

                    nearest_distance = distance
                    nearest_blocker = other


    return nearest_blocker


# =========================================================
# 15. 初始箭头数据
# =========================================================

arrows = [
    arrow.copy()
    for arrow in LEVELS[0]
]


# =========================================================
# 16. 主循环
# =========================================================

running = True


while running:

    update_layout()

    window_width, window_height = (
        screen.get_size()
    )


    # =====================================================
    # 17. 动态控件位置
    # =====================================================

    start_button = pygame.Rect(
        window_width // 2 - 110,
        window_height // 2 + 95,
        220,
        62
    )


    restart_button = pygame.Rect(
        window_width - 165,
        28,
        135,
        46
    )


    modal_button = pygame.Rect(
        window_width // 2 - 105,
        window_height // 2 + 80,
        210,
        58
    )


    # =====================================================
    # 18. 事件处理
    # =====================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False


        if event.type == pygame.VIDEORESIZE:

            screen = pygame.display.set_mode(
                (
                    event.w,
                    event.h
                ),
                pygame.RESIZABLE
            )

            update_layout()


        if event.type == pygame.MOUSEBUTTONDOWN:

            mouse_x, mouse_y = event.pos


            # -------------------------------------------------
            # 开始界面
            # -------------------------------------------------

            if game_state == "start":

                if start_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    start_new_game()

                continue


            # -------------------------------------------------
            # Game Over
            # -------------------------------------------------

            if game_state == "game_over":

                if modal_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    restart_current_level()

                continue


            # -------------------------------------------------
            # 关卡完成
            # -------------------------------------------------

            if game_state == "level_complete":

                if modal_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    go_to_next_level()

                continue


            # -------------------------------------------------
            # 全部关卡完成
            # -------------------------------------------------

            if game_state == "all_clear":

                if modal_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    start_new_game()

                continue


            # -------------------------------------------------
            # 游戏中
            # -------------------------------------------------

            if game_state == "playing":


                # Restart
                if restart_button.collidepoint(
                    mouse_x,
                    mouse_y
                ):

                    restart_current_level()

                    continue


                # 动画播放时禁止点击
                if (
                    flying_arrow is not None
                    or collision_arrow is not None
                ):

                    continue


                # 点击棋盘
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


                    if clicked_arrow is not None:

                        print(
                            "点击到了箭头：",
                            clicked_arrow
                        )


                        blocker = find_blocker(
                            clicked_arrow
                        )


                        # =====================================
                        # 被阻挡
                        # =====================================

                        if blocker is not None:

                            print(
                                "这个箭头被挡住了"
                            )

                            print(
                                "阻挡它的箭头：",
                                blocker
                            )


                            if mistakes_left > 0:

                                mistakes_left -= 1


                            print(
                                "剩余失误次数：",
                                mistakes_left
                            )


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


                            if mistakes_left == 0:

                                game_state = (
                                    "game_over"
                                )


                        # =====================================
                        # 可以飞出去
                        # =====================================

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


                            arrows.remove(
                                clicked_arrow
                            )


    # =====================================================
    # 19. 更新飞出动画
    # =====================================================

    if flying_arrow is not None:

        direction = (
            flying_arrow["direction"]
        )


        fly_speed = max(
            5,
            int(CELL_SIZE * 0.11)
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
    # 20. 更新碰撞动画
    # =====================================================

    collision_offset_x = 0
    collision_offset_y = 0


    if collision_arrow is not None:

        collision_frame += 1


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

            collision_offset_x = distance


        elif direction == "left":

            collision_offset_x = -distance


        elif direction == "up":

            collision_offset_y = -distance


        elif direction == "down":

            collision_offset_y = distance


        if (
            collision_frame
            >= COLLISION_TOTAL_FRAMES
        ):

            collision_arrow = None
            collision_blocker = None

            collision_frame = 0


    # =====================================================
    # 21. 判断关卡完成
    # =====================================================

    if (
        game_state == "playing"
        and len(arrows) == 0
        and flying_arrow is None
    ):

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


        else:

            game_state = (
                "all_clear"
            )

            print(
                "所有关卡全部完成"
            )


    # =====================================================
    # 22. 绘制背景
    # =====================================================

    screen.fill(
        BACKGROUND
    )


    # =====================================================
    # 23. 开始界面
    # =====================================================

    if game_state == "start":

        # -------------------------------------------------
        # 小装饰标题
        # -------------------------------------------------

        subtitle_top = small_font.render(
            "PUZZLE GAME",
            True,
            BLUE
        )

        subtitle_top_rect = (
            subtitle_top.get_rect(
                center=(
                    window_width // 2,
                    window_height // 2 - 145
                )
            )
        )

        screen.blit(
            subtitle_top,
            subtitle_top_rect
        )


        # -------------------------------------------------
        # 主标题
        # -------------------------------------------------

        title = title_font.render(
            "One More Arrow",
            True,
            TEXT_MAIN
        )

        title_rect = (
            title.get_rect(
                center=(
                    window_width // 2,
                    window_height // 2 - 85
                )
            )
        )

        screen.blit(
            title,
            title_rect
        )


        # -------------------------------------------------
        # 说明文字
        # -------------------------------------------------

        tip = info_font.render(
            "Clear every arrow without hitting blockers",
            True,
            TEXT_SECONDARY
        )

        tip_rect = (
            tip.get_rect(
                center=(
                    window_width // 2,
                    window_height // 2 - 10
                )
            )
        )

        screen.blit(
            tip,
            tip_rect
        )


        hint = small_font.render(
            "Choose the right order and escape the board",
            True,
            (135, 140, 150)
        )

        hint_rect = (
            hint.get_rect(
                center=(
                    window_width // 2,
                    window_height // 2 + 30
                )
            )
        )

        screen.blit(
            hint,
            hint_rect
        )


        draw_button(
            start_button,
            "Start Game",
            accent=True
        )


    # =====================================================
    # 24. 游戏界面
    # =====================================================

    else:

        # -------------------------------------------------
        # 页面标题
        # -------------------------------------------------

        header_title = big_font.render(
            "One More Arrow",
            True,
            TEXT_MAIN
        )

        screen.blit(
            header_title,
            (
                28,
                20
            )
        )


        # -------------------------------------------------
        # Restart
        # -------------------------------------------------

        draw_button(
            restart_button,
            "Restart"
        )


        # =================================================
        # 三个信息卡片
        # =================================================

        card_width = 150
        card_height = 68

        cards_total_width = (
            card_width * 3
            + 20 * 2
        )

        card_start_x = (
            window_width
            - cards_total_width
        ) // 2

        card_y = 100


        level_card = pygame.Rect(
            card_start_x,
            card_y,
            card_width,
            card_height
        )


        mistake_card = pygame.Rect(
            card_start_x
            + card_width
            + 20,
            card_y,
            card_width,
            card_height
        )


        remaining_card = pygame.Rect(
            card_start_x
            + (
                card_width
                + 20
            ) * 2,
            card_y,
            card_width,
            card_height
        )


        draw_info_card(
            level_card,
            "LEVEL",
            str(current_level + 1)
            + " / "
            + str(len(LEVELS)),
            BLUE
        )


        draw_info_card(
            mistake_card,
            "MISTAKES",
            str(mistakes_left)
            + " / "
            + str(MAX_MISTAKES),
            RED
        )


        draw_info_card(
            remaining_card,
            "REMAINING",
            str(len(arrows)),
            GREEN
        )


        # =================================================
        # 棋盘卡片背景
        # =================================================

        board_padding = 22

        board_card = pygame.Rect(
            BOARD_X - board_padding,
            BOARD_Y - board_padding,
            COLS * CELL_SIZE
            + board_padding * 2,
            ROWS * CELL_SIZE
            + board_padding * 2
        )


        draw_shadow_rect(
            board_card,
            radius=20,
            shadow_offset=7
        )


        pygame.draw.rect(
            screen,
            CARD_BG,
            board_card,
            border_radius=20
        )


        # =================================================
        # 绘制棋盘
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


                cell_rect = pygame.Rect(
                    x,
                    y,
                    CELL_SIZE,
                    CELL_SIZE
                )


                pygame.draw.rect(
                    screen,
                    (
                        252,
                        253,
                        255
                    ),
                    cell_rect
                )


                pygame.draw.rect(
                    screen,
                    GRID_COLOR,
                    cell_rect,
                    1
                )


        # =================================================
        # 绘制箭头
        # =================================================

        for arrow in arrows:

            if arrow is collision_arrow:

                draw_arrow(
                    screen,
                    arrow["row"],
                    arrow["col"],
                    arrow["direction"],
                    collision_offset_x,
                    collision_offset_y,
                    RED
                )


            else:

                draw_arrow(
                    screen,
                    arrow["row"],
                    arrow["col"],
                    arrow["direction"]
                )


        # =================================================
        # 飞出动画
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
        # 25. Game Over 弹窗
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
                OVERLAY_COLOR
            )

            screen.blit(
                overlay,
                (0, 0)
            )


            modal_width = min(
                450,
                window_width - 40
            )

            modal_height = 280


            modal_rect = pygame.Rect(
                window_width // 2
                - modal_width // 2,

                window_height // 2
                - modal_height // 2,

                modal_width,
                modal_height
            )


            draw_shadow_rect(
                modal_rect,
                radius=22,
                shadow_offset=8
            )


            pygame.draw.rect(
                screen,
                CARD_BG,
                modal_rect,
                border_radius=22
            )


            status_text = small_font.render(
                "TRY AGAIN",
                True,
                RED
            )


            status_rect = (
                status_text.get_rect(
                    center=(
                        window_width // 2,
                        window_height // 2 - 85
                    )
                )
            )


            screen.blit(
                status_text,
                status_rect
            )


            title = big_font.render(
                "Game Over",
                True,
                TEXT_MAIN
            )


            title_rect = (
                title.get_rect(
                    center=(
                        window_width // 2,
                        window_height // 2 - 35
                    )
                )
            )


            screen.blit(
                title,
                title_rect
            )


            message = small_font.render(
                "You used all available mistakes.",
                True,
                TEXT_SECONDARY
            )


            message_rect = (
                message.get_rect(
                    center=(
                        window_width // 2,
                        window_height // 2 + 15
                    )
                )
            )


            screen.blit(
                message,
                message_rect
            )


            draw_button(
                modal_button,
                "Restart",
                accent=True
            )


        # =================================================
        # 26. Level Complete
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
                OVERLAY_COLOR
            )

            screen.blit(
                overlay,
                (0, 0)
            )


            modal_width = min(
                470,
                window_width - 40
            )

            modal_height = 280


            modal_rect = pygame.Rect(
                window_width // 2
                - modal_width // 2,

                window_height // 2
                - modal_height // 2,

                modal_width,
                modal_height
            )


            draw_shadow_rect(
                modal_rect,
                radius=22,
                shadow_offset=8
            )


            pygame.draw.rect(
                screen,
                CARD_BG,
                modal_rect,
                border_radius=22
            )


            status_text = small_font.render(
                "SUCCESS",
                True,
                GREEN
            )


            status_rect = (
                status_text.get_rect(
                    center=(
                        window_width // 2,
                        window_height // 2 - 85
                    )
                )
            )


            screen.blit(
                status_text,
                status_rect
            )


            title = big_font.render(
                "Level Complete!",
                True,
                TEXT_MAIN
            )


            title_rect = (
                title.get_rect(
                    center=(
                        window_width // 2,
                        window_height // 2 - 35
                    )
                )
            )


            screen.blit(
                title,
                title_rect
            )


            message = small_font.render(
                "Great job. The next puzzle is waiting.",
                True,
                TEXT_SECONDARY
            )


            message_rect = (
                message.get_rect(
                    center=(
                        window_width // 2,
                        window_height // 2 + 15
                    )
                )
            )


            screen.blit(
                message,
                message_rect
            )


            draw_button(
                modal_button,
                "Next Level",
                accent=True
            )


        # =================================================
        # 27. 全部通关
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
                OVERLAY_COLOR
            )

            screen.blit(
                overlay,
                (0, 0)
            )


            modal_width = min(
                500,
                window_width - 40
            )

            modal_height = 300


            modal_rect = pygame.Rect(
                window_width // 2
                - modal_width // 2,

                window_height // 2
                - modal_height // 2,

                modal_width,
                modal_height
            )


            draw_shadow_rect(
                modal_rect,
                radius=22,
                shadow_offset=8
            )


            pygame.draw.rect(
                screen,
                CARD_BG,
                modal_rect,
                border_radius=22
            )


            status_text = small_font.render(
                "ALL CLEAR",
                True,
                GREEN
            )


            status_rect = (
                status_text.get_rect(
                    center=(
                        window_width // 2,
                        window_height // 2 - 100
                    )
                )
            )


            screen.blit(
                status_text,
                status_rect
            )


            title = big_font.render(
                "Congratulations!",
                True,
                TEXT_MAIN
            )


            title_rect = (
                title.get_rect(
                    center=(
                        window_width // 2,
                        window_height // 2 - 45
                    )
                )
            )


            screen.blit(
                title,
                title_rect
            )


            message = info_font.render(
                "You cleared all three levels.",
                True,
                TEXT_SECONDARY
            )


            message_rect = (
                message.get_rect(
                    center=(
                        window_width // 2,
                        window_height // 2 + 10
                    )
                )
            )


            screen.blit(
                message,
                message_rect
            )


            draw_button(
                modal_button,
                "Play Again",
                accent=True
            )


    # =====================================================
    # 28. 刷新屏幕
    # =====================================================

    pygame.display.flip()

    clock.tick(60)


# =========================================================
# 29. 退出
# =========================================================

pygame.quit()