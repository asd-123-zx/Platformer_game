import os
import random
import math
import pygame
from os import listdir
from os.path import isfile, join


pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_VEL = 5
GRAVITY = 1

window = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.Font(None, 74)


GAME_OVER_BG = pygame.image.load(join("Assets", "Backgrounds", "game_over.png"))  # Update path as needed
GAME_OVER_BG = pygame.transform.scale(GAME_OVER_BG, (WIDTH, HEIGHT))

JUMP_HEIGHT = -GRAVITY * 8  # Vertical velocity during jump
# Calculate maximum jump distance
# Time to reach the peak of the jump: t = -vy / gravity
time_to_peak = -JUMP_HEIGHT / GRAVITY
# Total jump time (up and down): t_total = 2 * time_to_peak
total_jump_time = 2 * time_to_peak
# Maximum horizontal distance: distance = vx * t_total
MAX_JUMP_DISTANCE = PLAYER_VEL * total_jump_time

class SoundManager:
    def __init__(self):
        self.sounds = {
            "background": None,
            "jump": None,
            "fall": None,
            "game_over": None,
        }

    def load_sounds(self, sound_dir):
        """Load all sound files from the specified directory."""
        self.sounds["background"] = pygame.mixer.Sound(join(sound_dir, "Ground_Theme.mp3"))
        self.sounds["jump"] = pygame.mixer.Sound(join(sound_dir, "jump_up.mp3"))
        self.sounds["fall"] = pygame.mixer.Sound(join(sound_dir, "Game_Over.mp3"))
        self.sounds["coin"] = pygame.mixer.Sound(join(sound_dir, "Winning a coin.wav"))
        self.sounds["game_over"] = pygame.mixer.Sound(join(sound_dir, "Game_Over.mp3"))

    def play_background(self):
        """Play background music on loop."""
        self.sounds["background"].play(-1)  # -1 means loop indefinitely

    def play_jump(self):
        """Play jump sound."""
        self.sounds["jump"].play()

    def play_fall(self):
        """Play fall sound."""
        self.sounds["fall"].play()
    
    def coin(self):
        """Play coin sound."""
        self.sounds["coin"].play()


    def play_game_over(self):
        """Play game over music."""
        self.sounds["game_over"].play()

    def stop_background(self):
        """Stop background music."""
        self.sounds["background"].stop()

# Initialize Sound Manager
sound_manager = SoundManager()
sound_manager.load_sounds("Sound_Effects") 





def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
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


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 64, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("Character", "", 32, 32, True)
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
        self.dead = False  # New flag for player death


    def jump(self):
        self.y_vel = -self.GRAVITY * 8
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        self.hit = True

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        self.y_vel += min(1, (self.fall_count / fps) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > fps * 2:
            self.hit = False
            self.hit_count = 0

        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count == 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, name=None):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.width = width
        self.height = height
        self.name = name

    def draw(self, win, offset_x):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y))


class Block(Object):
    def __init__(self, x, y, size):
        super().__init__(x, y, size, size)
        block = get_block(size)
        self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)

class Checkpoint(Object):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "checkpoint")
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (0, 255, 0), (0, 0, width, height))  # Green checkpoint

class Fire(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "fire")
        self.fire = load_sprite_sheets("Traps", "Fire", width, height)
        self.image = self.fire["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.fire[self.animation_name]
        sprite_index = (self.animation_count //
                        self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1

        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


def get_background(name):
    image = pygame.image.load(join("Assets", "Backgrounds", name))
    _, _, width, height = image.get_rect()
    tiles = []

    for i in range(WIDTH // width + 1):
        for j in range(HEIGHT // height + 1):
            pos = (i * width, j * height)
            tiles.append(pos)

    return tiles, image
def draw(window, background, bg_image, player, objects, offset_x, score):
    # Draw the background
    for tile in background:
        window.blit(bg_image, tile)

    # Draw objects
    for obj in objects:
        obj.draw(window, offset_x)

    # Draw the player
    player.draw(window, offset_x)

    # Draw the score (always on top)
    score_font = pygame.font.SysFont("Arial", 36)  # Font for the score
    score_text = score_font.render(f"Score: {score}", True, (255, 255, 255))  # White text
    window.blit(score_text, (WIDTH - 200, 20))  # Upper-right corner

    # Update the display
    pygame.display.update()

def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

                collided_objects.append(obj)

    return collided_objects

def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if obj.name == "coin":  # Skip collision checks for coins
            continue
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object

def handle_move(player, objects):
    keys = pygame.key.get_pressed()
    player_dead = False

    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)
         
    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)
      

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]
    
    for obj in to_check:
        if obj and obj.name == "fire":
            player.make_hit()
            sound_manager.play_fall()
            player.dead = True  # Mark player as dead
    return player_dead


class Coin(Object):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height, "coin")
        self.image = pygame.image.load(join("Assets", "Cherries.png")).convert_alpha()
        self.image = pygame.transform.scale(self.image, (width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.collected = False
        self.mask = pygame.mask.from_surface(self.image)  # Ensure the coin has a valid mask

    def update(self, player):
        if not self.collected and self.rect.colliderect(player.rect):  # Use simple rect collision
            self.collected = True
            sound_manager.coin()  # Play coin collection sound
            return True
        return False

# Generate random terrain for Level 1
def create_random_level_1():
    block_size = 96
    player = Player(100, 100, 50, 50)
    floor = []
    objects = []


    # Define level length and pit constraints
    level_length = (WIDTH * 20) // block_size  # Longer level
    max_gap_size = max(1, int(MAX_JUMP_DISTANCE // block_size))  # Maximum allowable gap size
    

    for _ in range(10):
        x = random.randint(500, level_length * block_size - 500)
        y = random.randint(HEIGHT // 2, HEIGHT - block_size * 2)
        objects.append(Coin(x, y, 32, 32))




    # Generate random platforms with balanced distribution
    for i in range(-WIDTH // block_size, level_length):
        if i % 5 == 0 or random.random() < 0.5:  # Ensure blocks appear regularly
            floor.append(Block(i * block_size, HEIGHT - block_size, block_size))
        else:
            # Create a pit with a limited gap size
            if i > 0 and i + max_gap_size < level_length:
                gap_size = random.randint(1, max_gap_size)
                for j in range(gap_size):
                    floor.append(None)  # Add gaps
                i += gap_size - 1  # Skip over the gap
            else:
                floor.append(Block(i * block_size, HEIGHT - block_size, block_size))  # Fill gap if invalid

    # Add floating platforms and fire traps
    for i in range(5, level_length - 5):  # Avoid edges
        if random.random() < 0.3:  # Add floating platforms
            y = HEIGHT - block_size * random.randint(2, 4)
            objects.append(Block(i * block_size, y, block_size))

        if random.random() < 0.3:  # Add fire traps with more uniform distribution
            y = HEIGHT - block_size - 64
            fire = Fire(i * block_size, y, 16, 32)
            fire.on()
            objects.append(fire)

    # Add a checkpoint at the end with a clear path
    checkpoint_x = level_length * block_size - block_size * 5  # Near the end
    checkpoint = Checkpoint(checkpoint_x, HEIGHT - block_size * 2, block_size, block_size)
    objects.append(checkpoint)

    # Ensure a clear path near the checkpoint
    for i in range(level_length - 10, level_length):  # Clear path for the last few blocks
        floor[i] = Block(i * block_size, HEIGHT - block_size, block_size)

    # Remove None values from the floor list
    floor = [obj for obj in floor if obj is not None]
    objects.extend(floor)

    return player, objects


# Predefined Level 2
def create_level_2():
    block_size = 96
    player = Player(100, 100, 50, 50)
    fire = Fire(500, HEIGHT - block_size - 64, 16, 32)
    fire.on()
    floor = [Block(i * block_size, HEIGHT - block_size, block_size)
             for i in range(-WIDTH // block_size, (WIDTH * 25) // block_size)]  # Longer level
    # Create multiple pits
    for i in range(10, 15):  # Pit 1
        floor[i] = None
    for i in range(20, 25):  # Pit 2
        floor[i] = None
    # Add more fire traps
    for i in range(5, 25):
        if random.random() < 0.4:  # 30% chance to add a fire trap
            y = HEIGHT - block_size - 64
            fire = Fire(i * block_size, y, 16, 32)
            fire.on()
            objects.append(fire)
    # Add a checkpoint
    checkpoint = Checkpoint(WIDTH * 22, HEIGHT - block_size * 2, block_size, block_size)
    objects = [*floor, Block(block_size * 2, HEIGHT - block_size * 2, block_size),
               Block(block_size * 5, HEIGHT - block_size * 4, block_size),
               Block(block_size * 8, HEIGHT - block_size * 3, block_size),
               Block(block_size * 12, HEIGHT - block_size * 2, block_size), fire, checkpoint]
    # Remove None values from the floor list
    objects = [obj for obj in objects if obj is not None]
    return player, objects

# Game over logic
def check_game_over(player, objects):
    return player.dead or player.rect.y > HEIGHT

def display_message(window, message, bg_image=None):
    if bg_image:
        window.blit(bg_image, (0, 0))  # Display the background image
    else:
        window.fill((0, 0, 0))  # Clear the screen with a black background

    # Render the message
    font = pygame.font.SysFont("Arial", 74)
    text = font.render(message, True, (255, 255, 255))  # White text
    text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    window.blit(text, text_rect)

    pygame.display.update()
    pygame.time.delay(2000) 

# Main game loop
def main(window):
    clock = pygame.time.Clock()
    background, bg_image = get_background("Brown.png")

    levels = [create_random_level_1, create_level_2]
    current_level = 0
    player, objects = levels[current_level]()

    offset_x = 0
    scroll_area_width = 200
    coin_count = 0  # Track collected coins
    score = 0  # Initialize score

    # Play entrance music
    pygame.time.delay(2000)
    sound_manager.play_background()

    run = True
    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 2:
                    player.jump()
                    sound_manager.play_jump()

        player.loop(FPS)
        for obj in objects:
            if isinstance(obj, Fire):
                obj.loop()

        player_dead = handle_move(player, objects)

        # Update coins and score
        for obj in objects[:]:  # Iterate over a copy to allow removal
            if isinstance(obj, Coin):
                if obj.update(player):
                    objects.remove(obj)  # Remove collected coins
                    coin_count += 1  # Increment coin count
                    score += 10  # Increment score by 10 for each coin
                    print(f"Coins collected: {coin_count}, Score: {score}")  # Debugging output

        # Draw everything, including the score
        draw(window, background, bg_image, player, objects, offset_x, score)

        if check_game_over(player, objects) or player_dead:
            sound_manager.stop_background()
            sound_manager.play_game_over()
            display_message(window, f"Game Over! Score: {score}", GAME_OVER_BG)  # Show score on game over screen
            return  # Return to the front page

        # Check for checkpoint collision
        for obj in objects:
            if obj.name == "checkpoint" and pygame.sprite.collide_mask(player, obj):
                display_message(window, f"Level {current_level + 1} Completed! Score: {score}")
                current_level += 1
                if current_level >= len(levels):
                    display_message(window, f"Game Completed! Final Score: {score}")
                    return  # Return to the front page
                else:
                    player, objects = levels[current_level]()
                    offset_x = 0

        if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
                (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
            offset_x += player.x_vel

    pygame.quit()
    quit()