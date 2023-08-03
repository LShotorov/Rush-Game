import pygame
import button
import level_editor
import play
from os import listdir


def draw_background(background: pygame.image) -> None:
    window.blit(background, (0, 0))

def draw_text(text: str, size: int, font: str, text_color: tuple, x: int, y: int) -> None:
    font = pygame.font.SysFont(f"{font}", size)
    image = font.render(text, True, text_color)
    window.blit(image, (x, y))

def create_buttons(path: str) -> list:
    button_list = []
    text_list = []
    button_column = 0
    button_row = 0
    for i in range(len(listdir(path))):
        level_button = button.Button(WIDTH // 3 + (75 * button_column), 75 * button_row + 405, level_image, 1)
        button_list.append(level_button)
        text_list.append([f"{i}", 50, "Futura", WHITE, WIDTH // 3 + (75 * button_column) + 17, 75 * button_row + 410])
        button_column += 1
        if button_column == 5:
            button_row += 1
            button_column = 0
    
    return button_list, text_list


clock = pygame.time.Clock()
FPS = 60

WIDTH, HEIGHT = 1280, 720
LOWER_MARGIN, SIDE_MARGIN = 100, 300
ROWS, MAX_COLUMNS = 16, 150
TILE_SIZE = HEIGHT // ROWS
TILE_TYPES = 19
WHITE = (255, 255, 255)
GRAY = (115, 115, 115)
RED = (205, 20, 20)

level = 0

window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rush")

background = pygame.image.load("Background/background.png").convert_alpha()
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

play_image = pygame.image.load("Buttons/play.png").convert_alpha()
level_editor_image = pygame.image.load("Buttons/level_editor.png").convert_alpha()
quit_image = pygame.image.load("Buttons/quit.png").convert_alpha()
level_image = pygame.image.load("Buttons/level.png").convert_alpha()

play_button = button.Button(WIDTH // 2.2, HEIGHT // 2, play_image, 1)
level_editor_button = button.Button(WIDTH // 2.2, HEIGHT // 2 + 75, level_editor_image, 1)
quit_button = button.Button(WIDTH // 2.2, HEIGHT  // 2 + 150, quit_image, 1)


tiles = [pygame.transform.scale(
    pygame.image.load(f"Tiles/{i}.png").convert_alpha(),(TILE_SIZE, TILE_SIZE)
    )
    for i in range(TILE_TYPES)
]


menu = "main"
run = True
while run:
    pygame.init()
    clock.tick(FPS)
    draw_background(background)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
            break
    
    if menu == "main":
        pygame.display.set_caption("Rush")
        draw_text("R U S H", 200, "Futura", GRAY, WIDTH // 3, HEIGHT // 4)
        draw_text("R U S H", 195, "Futura", RED, WIDTH // 3 + 5, HEIGHT // 4 + 3)
        if play_button.draw(window):
            menu = "choose_level"

        if level_editor_button.draw(window):
            menu = "level_editor"
    
        if quit_button.draw(window):
            run = False
            break

    elif menu == "choose_level":
        draw_text("Choose Level", 150, "Futura", GRAY, WIDTH // 4, HEIGHT // 4)
        draw_text("Choose Level", 149, "Futura", RED, WIDTH // 4 + 3, HEIGHT // 4 + 3)

        button_list, text_list = create_buttons("Levels")

        for button_count, a_button in enumerate(button_list):
            if a_button.draw(window):
                level = button_count
                menu = "play"

            draw_text(text_list[button_count][0],
                        text_list[button_count][1],
                        text_list[button_count][2],
                        text_list[button_count][3],
                        text_list[button_count][4],
                        text_list[button_count][5]
                    )


    elif menu == "play":
        if play.play(WIDTH, HEIGHT, level, TILE_SIZE):
            menu = "main"
    
    elif menu == "level_editor":
        if level_editor.edit_level(WIDTH, HEIGHT, LOWER_MARGIN, SIDE_MARGIN):
            menu = "main"

    pygame.display.update()


pygame.quit()
quit()