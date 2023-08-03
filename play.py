import pygame
import pickle
from os import listdir
from os.path import isfile, join


def flip(sprites: list) -> list:
    """
    Flip a list of sprites horizontally.

    Args:
        sprites (list): A list of sprites to flip.

    Returns:
        A list of flipped sprites.
    """

    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]



def load_sprites(path: str, width: int, height: int, direction: bool = False) -> dict:
    """
    Load a dictionary of sprites from a directory of images.

    Args:
        path (str): The path to the directory of images.
        width (int): The width of each sprite.
        height (int): The height of each sprite.
        direction (bool): Whether to load sprites for both left and right directions.

    Returns:
        A dictionary of sprites.
    """

    images = [f for f in listdir(path) if isfile(join(path, f))]
    all_sprites = {}
    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()
        
        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            sprites.append(pygame.transform.scale2x(surface))
        
        if direction:
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites



def draw_level(window: pygame.display, objects: list, offset_x: int) -> None:
    """
    Draw a level on a window.

    Args:
        window (pygame.display): The window to draw on.
        objects (list): A list of objects to draw.
        offset_x (int): The x-offset of the level.

    Returns:
        None
    """

    for i in objects:
        window.blit(i.image, (i.rect.x - offset_x, i.rect.y))




def get_background(name: str, width: int, height: int) -> pygame.image:
    """
    Load a background image.

    Args:
        name (str): The name of the image file.
        width (int): The width of the image.
        height (int): The height of the image.

    Returns:
        A pygame image object.
    """

    image = pygame.image.load(join("Background", name))
    image = pygame.transform.scale(image, (width, height))

    return image




def draw(window: pygame.display, background: pygame.image, life_img: pygame.image, player, offset_x: int, objects: list) -> None:
    """
    Draw the game screen.

    Args:
        window (pygame.display): The game window.
        background (pygame.image): The background image.
        life_img (pygame.image): The life image.
        player (Player): An instance of the Player class.
        offset_x (int): The x offset of the screen.
        objects (list): A list of objects to draw.

    Returns:
        None
    """
    window.blit(background, (0, 0))
    draw_level(window, objects, offset_x)
    window.blit(life_img, (70, 20))
    player.draw(window, offset_x)
    pygame.display.update()

def handle_vertical_collision(player, objects: list, dy: int) -> list:
    """
    Handle vertical collision between a player and a list of objects.

    Args:
        player (Player): An instance of the Player class.
        objects (list): A list of objects to check for collision.
        dy (int): The change in y-position of the player.

    Returns:
        A list of collided objects.
    """

    collided_objects = []
    for object in objects:
        if pygame.sprite.collide_mask(player, object):
            if dy > 0:
                player.rect.bottom = object.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = object.rect.bottom
                player.hit_head()
        
            collided_objects.append(object)

    return collided_objects




def collide(player, objects: list, dx: int) -> pygame.sprite.Sprite:
    """
    Check for collision between a player and a list of objects.

    Args:
        player (Player): An instance of the Player class.
        objects (list): A list of objects to check for collision.
        dx (int): The change in x-position of the player.

    Returns:
        The first object in objects that collides with player or None if there is no collision.
    """

    player.move(dx, 0)
    player.update()
    collided_object = next(
        (
            object
            for object in objects
            if pygame.sprite.collide_mask(player, object)
        ),
        None,
    )
    player.move(-dx, 0)
    player.update()

    return collided_object



def get_mask(tile_number: int, tile_size: int, x_pos: int, y_pos: int) -> pygame.sprite.Sprite:
    """
    Returns a Pygame sprite object with an image loaded from a file.

    Args:
        tile_number (int): The number of the tile to load.
        tile_size (int): The size of the tile in pixels.
        x_pos (int): The x position of the tile on the screen.
        y_pos (int): The y position of the tile on the screen.

    Returns:
        A pygame sprite object.
    """

    tile_image = pygame.image.load(f"Tiles/{tile_number}.png").convert_alpha()
    tile_image = pygame.transform.scale(tile_image, (tile_size, tile_size))
    tile = pygame.sprite.Sprite()
    tile.image = tile_image
    tile.rect = tile_image.get_rect()
    tile.rect.x = x_pos * tile_size
    tile.rect.y = y_pos * tile_size
    tile.mask = pygame.mask.from_surface(tile_image)

    return tile



def handle_move(player, objects: list, player_vel: int, height: int, enemies: list, water: list) -> None:
    """
    Handles player movement and collision detection.

    Args:
        player (Player): An instance of the Player class.
        objects (list): A list of objects that can be collided with.
        player_vel (int): The velocity of the player.
        height (int): The height of the screen.
        enemies (list): A list of enemy objects.
        water (list): A list of water objects.

    Returns:
        None
    """

    keys = pygame.key.get_pressed()

    player.x_vel = 0
    collide_left = collide(player, objects, -player_vel * 2)
    collide_right = collide(player, objects, player_vel * 2)

    if keys[pygame.K_LEFT] and not collide_left and not player.hit:
        player.move_left(player_vel)
    if keys[pygame.K_RIGHT] and not collide_right and not player.hit:
        player.move_right(player_vel)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    for object in to_check:
        if object:
            if object in enemies:
                player.make_hit()
            elif object in water:
                player.rect.y += 18
                player.y_vel += 10
                player.make_hit()
    
    if player.rect.y > height:
        player.make_hit()



def get_objects(level: int, obj_tile_numbers: list, tile_size: int) -> list:
    """
    Returns a list of pygame sprite objects.

    Args:
        level (int): The level number to load.
        obj_tile_numbers (list): A list of tile numbers to check the type of the tile.
        tile_size (int): The size of each tile in pixels.

    Returns:
        A list of pygame sprite objects.
    """

    objects = []
    level_data = pickle.load(open(f"Levels/level_{level}", "rb"))
    for y_pos, row in enumerate(level_data):
        objects.extend(
            get_mask(tile, tile_size, x_pos, y_pos)
            for x_pos, tile in enumerate(row)
            if tile > -1 and tile in obj_tile_numbers
        )

    return objects



class Player(pygame.sprite.Sprite):
    """
    A class representing a player object.

    Attributes:
        GRAVITY (int): The strength of gravity applied to the player.
        SPRITES (dict): A dictionary containing all of the player's sprites.
        ANIMATION_DELAY (int): The delay between animation frames.

    Methods:
        __init__(self, x, y, width, height): Initializes a new instance of the Player class.
        jump(self): Makes the player jump.
        move(self, dx, dy): Moves the player by dx and dy pixels.
        move_left(self, vel): Moves the player left by vel pixels.
        move_right(self, vel): Moves the player right by vel pixels.
        make_hit(self): Sets the hit attribute to True.
        loop(self, fps): Updates the player's position and sprite animation.
        landed(self): Resets fall_count and jump_count attributes when player lands on a surface.
        hit_head(self): Resets fall_count and inverts y_vel attribute when player hits their head on a surface.
        update_sprite(self): Updates the sprite animation based on current state of player object.
        update(self): Updates the position and mask attributes of the sprite object.
        draw(self, win, offset_x): Draws the sprite object onto a window surface.
    """

    GRAVITY = 1
    SPRITES = {}
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0

    def jump(self) -> None:
        """
        Makes the player jump.
        """
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx: int, dy: int) -> None:
        """
        Moves the player by dx and dy pixels.

        Args:
            dx (int): The number of pixels to move horizontally.
            dy (int): The number of pixels to move vertically.

        Returns:
            None
        """
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel: int) -> None:
        """
        Moves the player left by vel pixels.

        Args:
            vel (int): The number of pixels to move left.

        Returns:
            None
        """
        self.x_vel = - vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel: int) -> None:
        """
        Moves the player right by vel pixels.

        Args:
            vel (int): The number of pixels to move right.

        Returns:
            None
        """
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def make_hit(self) -> None:
        """
        Sets the hit attribute to True.
        """
        self.hit = True

    def loop(self, fps: int) -> None:
        """
        Updates the player's position and sprite animation.

        Args:
            fps (int): The frames per second of the game.

        Returns:
            None
        """

        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps // 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        """
        Resets fall_count and jump_count attributes when player lands on a surface.
        """
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        """
        Resets fall_count and inverts y_vel attribute when player hits their head on a surface.
        """
        self.fall_count = 0
        self.y_vel *= -1

    def update_sprite(self):
        """
        Updates the sprite animation based on current state of player object.
        """

        sprite_name = "idle"
        if self.hit:
            sprite_name = "hit" 
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_name = "jump"
            elif self.jump_count == 2:
                sprite_name = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_name = "fall"
        elif self.x_vel != 0:
            sprite_name = "run"


        sprites = self.SPRITES[f"{sprite_name}_{self.direction}"]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()


    def update(self):
        """
        Updates the position and mask attributes of the sprite object.
        """
        self.rect = self.sprite.get_rect(topleft = (self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win: pygame.display, offset_x: int) -> None:
        """
        Draws the sprite object onto a window surface.

        Args:
            win (pygame.display): The display to draw the player's sprite onto.
            offset_x (int): The x-coordinate offset of the screen.
        
        Returns:
            None
        """
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))



def play(width: int, height: int, level: int, tile_size: int) -> bool:
    """
    Runs the game loop for the game.

    Args:
        width (int): The width of the game window.
        height (int): The height of the game window.
        level (str): The level number to load.
        tile_size (int): The size of each tile in pixels.

    Returns:
        True if game over, False otherwise.
    """

    pygame.init()
    pygame.display.set_caption("Rush")

    window = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    background = get_background("background.png", width, height)
    life_img = get_background("life.png", 40, 32)

    FPS = 60
    PLAYER_VEL = 6
    offset_x = 0

    player = Player(100, 100, 50, 50)
    player.SPRITES = load_sprites("Player", 32, 32, True)
    tiles = get_objects(level, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 15, 16, 17], tile_size)
    enemies = get_objects(level, [14, 18], tile_size)
    water = get_objects(level, [12, 13], tile_size)

    objects = enemies + tiles + water
    scroll_area_width = 400

    game_over = [False, 40]
    play = True
    while play:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                play = False
                break

            if (
                event.type == pygame.KEYDOWN
                and event.key == pygame.K_UP
                and player.jump_count < 2
                and not player.hit
            ):
                player.jump()

        player.loop(FPS)
        handle_move(player, objects, PLAYER_VEL, height, enemies, water)
        draw(window, background, life_img, player, offset_x, objects)


        if ((player.rect.right - offset_x >= width - scroll_area_width) and player.x_vel > 0) or \
                ((player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

        if player.hit:
            game_over[0] = True
        if game_over[0]:
            game_over[1] -= 1
        if game_over[1] == 0:
            play = False
            return True

    pygame.quit()
    quit()