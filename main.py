import pygame

pygame.init()

screen = pygame.display.set_mode((800, 600))

ROWS = 5
COLS = 5
CELL_SIZE = 80

BOARD_X = 200
BOARD_Y = 100


def draw_arrow(screen, row, col, direction):
    center_x = BOARD_X + col * CELL_SIZE + CELL_SIZE // 2
    center_y = BOARD_Y + row * CELL_SIZE + CELL_SIZE // 2

    body_length = 25
    head_size = 10

    if direction == "right":
        start = (center_x - body_length, center_y)
        end = (center_x + body_length, center_y)

        pygame.draw.line(screen, (0, 0, 0), start, end, 4)
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

    elif direction == "left":
        start = (center_x + body_length, center_y)
        end = (center_x - body_length, center_y)

        pygame.draw.line(screen, (0, 0, 0), start, end, 4)
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

    elif direction == "up":
        start = (center_x, center_y + body_length)
        end = (center_x, center_y - body_length)

        pygame.draw.line(screen, (0, 0, 0), start, end, 4)
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

    elif direction == "down":
        start = (center_x, center_y - body_length)
        end = (center_x, center_y + body_length)

        pygame.draw.line(screen, (0, 0, 0), start, end, 4)
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


arrows = [
    {"row": 0, "col": 0, "direction": "right"},
    {"row": 1, "col": 3, "direction": "down"},
    {"row": 3, "col": 1, "direction": "left"},
    {"row": 4, "col": 4, "direction": "up"}
]

running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((255, 255, 255))

    for row in range(ROWS):
        for col in range(COLS):
            x = BOARD_X + col * CELL_SIZE
            y = BOARD_Y + row * CELL_SIZE

            pygame.draw.rect(
                screen,
                (0, 0, 0),
                (x, y, CELL_SIZE, CELL_SIZE),
                1
            )

    for arrow in arrows:
        draw_arrow(
            screen,
            arrow["row"],
            arrow["col"],
            arrow["direction"]
        )

    pygame.display.flip()

pygame.quit()