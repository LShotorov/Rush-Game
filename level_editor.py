import pygame
import button
import pickle

def draw_text(window, text, font, text_color, x, y):
    image = font.render(text, True, text_color)
    window.blit(image, (x, y))

def draw_background(window, color, background, width, scroll):
    window.fill(color)
    for x in range(6):
        window.blit(background, ((x * width) - scroll, 0))

def draw_grid(window, color, columns, rows, width, height, tile_size, scroll):
    for c in range(columns + 1):
        pygame.draw.line(window, color, (c * tile_size - scroll, 0), (c * tile_size - scroll, height))

    for c in range(rows + 1):
        pygame.draw.line(window, color, (0, c * tile_size), (width, c * tile_size))


def draw_level(window, level_data, tiles, tile_size, scroll):
    for y, row in enumerate(level_data):
        for x, tile in enumerate(row):
            if tile > -1:
                window.blit(tiles[tile], (x * tile_size - scroll, y * tile_size))



def edit_level(width, height, lower_margin, side_margin):

    clock = pygame.time.Clock()
    FPS = 60

    BACKGROUND_COLOR = (106, 181, 111)
    WHITE = (255, 255, 255)
    GRAY = (115, 115, 115)
    RED = (205, 20, 20)
    ROWS, MAX_COLUMNS = 16, 150
    TILE_SIZE = height // ROWS
    TILE_TYPES = 19

    font = pygame.font.SysFont("Futura", 30)
    current_tile = 0
    level = 0
    scroll_left = False
    scroll_right = False
    scroll = 0
    scroll_speed = 1

    window = pygame.display.set_mode((width + side_margin, height + lower_margin))
    pygame.display.set_caption("Level Editor")

    background = pygame.image.load("Background/background.png").convert_alpha()
    background = pygame.transform.scale(background, (width, height))

    tiles = []
    for i in range(TILE_TYPES):
        image = pygame.image.load(f"Tiles/{i}.png").convert_alpha()
        image = pygame.transform.scale(image, (TILE_SIZE, TILE_SIZE))
        tiles.append(image)

    save_image = pygame.image.load("Buttons/save.png").convert_alpha()
    load_image = pygame.image.load("Buttons/load.png").convert_alpha()
    back_image = pygame.image.load("Buttons/back.png").convert_alpha()

    level_data = []
    for _ in range(ROWS):
        r = [-1] * MAX_COLUMNS
        level_data.append(r)

    save_button = button.Button(width // 2, height + lower_margin - 75, save_image, 1)
    load_button = button.Button(width // 2 + 200, height + lower_margin - 75, load_image, 1)
    back_button = button.Button(width // 2 + 650, height + lower_margin - 75, back_image, 1)

    button_list = []
    button_column = 0
    button_row = 0
    for i in range(len(tiles)):
        tile_button = button.Button(width + (75 * button_column) + 50, 75 * button_row + 50, tiles[i], 1)
        button_list.append(tile_button)
        button_column += 1
        if button_column == 3:
            button_row += 1
            button_column = 0

    save_count = 0
    load_count = 0
    run = True
    while run:
        
        clock.tick(FPS)
        draw_background(window, BACKGROUND_COLOR, background, width, scroll)
        draw_grid(window, GRAY, MAX_COLUMNS, ROWS, width, height, TILE_SIZE, scroll)
        draw_level(window, level_data, tiles, TILE_SIZE, scroll)

        draw_text(window, f"Level: {level}", font, WHITE, 10, height + lower_margin - 90)
        draw_text(window, "Press LEFT or RIGHT to scroll  //  Hold SHIFT to scroll faster", font, WHITE, 10, height + lower_margin - 60)
        draw_text(window, "Press UP or DOWN to change level", font, WHITE, 10, height + lower_margin - 30)
        draw_text(window, "Left-click to draw", font, WHITE, width - side_margin + 80, height + lower_margin - 70)
        draw_text(window, "Right-click to delete", font, WHITE, width - side_margin + 80, height + lower_margin - 40)

        if back_button.draw(window):
            window = pygame.display.set_mode((width, height))
            run = False
            return True
        if save_button.draw(window):
            with open(f"Levels/level_{level}", "wb") as pickle_out:
                pickle.dump(level_data, pickle_out)
            load_count = 0
            save_count = 120
        if save_count != 0:
            draw_text(window, f"Level_{level} saved successfully", font, WHITE, width // 2 + 50, height + lower_margin - 25)
            save_count -= 1

        if load_button.draw(window):
            scroll = 0
            level_data = []
            pickle_in = open(f"Levels/level_{level}", "rb")
            level_data = pickle.load(pickle_in)
            save_count = 0
            load_count = 120
        if load_count != 0:
            draw_text(window, f"Level_{level} loaded", font, WHITE, width // 2 + 50, height + lower_margin - 25)
            load_count -= 1


        pygame.draw.rect(window, BACKGROUND_COLOR, (width, 0, side_margin, height + 1))

        for button_count, i in enumerate(button_list):
            if i.draw(window):
                current_tile = button_count

        pygame.draw.rect(window, RED, button_list[current_tile].rect, 3)

        if scroll_left and scroll > 0:
            scroll -= 5 * scroll_speed
        if scroll_right and scroll < (MAX_COLUMNS * TILE_SIZE) - width:
            scroll += 5 * scroll_speed

        pos = pygame.mouse.get_pos()
        x = (pos[0] + scroll) // TILE_SIZE
        y = pos[1] // TILE_SIZE

        if pos[0] < width and pos[1] < height:
            if pygame.mouse.get_pressed()[0] and level_data[y][x] != current_tile:
                level_data[y][x] = current_tile
            if pygame.mouse.get_pressed()[2]:
                level_data[y][x] = -1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    level += 1
                if event.key == pygame.K_DOWN and level > 0:
                    level -= 1
                if event.key == pygame.K_LEFT:
                    scroll_left = True
                if event.key == pygame.K_RIGHT:
                    scroll_right = True
                if event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                    scroll_speed = 5

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    scroll_left = False
                if event.key == pygame.K_RIGHT:
                    scroll_right = False
                if event.key in [pygame.K_LSHIFT, pygame.K_RSHIFT]:
                    scroll_speed = 1


        pygame.display.update()


    pygame.quit()
    quit()

