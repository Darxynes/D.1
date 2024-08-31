#by Yana Parkhomenko

from pygame import *
from math import sqrt

init()

clock = time.Clock()

# Load images
wall_image = image.load("wall.jpg")
player_image = image.load("OCONEL.png")
background_image = image.load("bc.jpg")
blur_background_image = image.load("blur_bc.jpg")
enemy_MUMMY_image = image.load("IMHOTEB.png")
enemy_NOSY_image = image.load("UWIXLY.png")
bullet_image = image.load("TNT.png")
FIVANSKIE_SVITKY_image = image.load("FIVANTSKIE_SVITKY.png")

# Sounds
bullet_sound = mixer.Sound("dinamit.mp3")
bullet_sound.set_volume(0.2)

death_effect = mixer.Sound("go.mp3")
death_effect.set_volume(0.2)

win_sound = mixer.Sound("pobeda.mp3")
win_sound.set_volume(0.2)

run_sound = mixer.Sound("zvuk_-_shagov.mp3")
run_sound.set_volume(0.2)

bc_sound = mixer.Sound("Egipet.mp3")
bc_sound.set_volume(0.4)
bc_sound.play()

# Window setup
window = display.set_mode((800, 600))
display.set_caption("L.I.T.P")#лабиринт в пирамиде

# Class: Sprite
class GameSprite(sprite.Sprite):
    def __init__(self, image, x, y, w, h):
        super().__init__()
        self.image = transform.scale(image, (w, h))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = mask.from_surface(self.image)  # Create a mask from the image
        self.flip = False

    # Drawing
    def draw(self):
        window.blit(transform.flip(self.image, self.flip, False), (self.rect.x, self.rect.y))

# Class: Player
class Player(GameSprite):
    def __init__(self, image, x, y, w, h, speed_x, speed_y):
        super().__init__(image, x, y, w, h)
        self.speed_x = speed_x
        self.speed_y = speed_y

    # Shooting
    def fire(self):
        if self.flip:
            bullet = Bullet(bullet_image, self.rect.left, self.rect.centery, 30, 30, 10, 0)
        else:
            bullet = Bullet(bullet_image, self.rect.right, self.rect.centery, 30, 30, -10, 0)
        bullets.add(bullet)

    # Move player
    def update(self):
        keys = key.get_pressed()

        new_x = self.rect.x
        new_y = self.rect.y

        if keys[K_LEFT]:
            new_x -= self.speed_x
            self.flip = False

        if keys[K_RIGHT]:
            new_x += self.speed_x
            self.flip = True

        if keys[K_UP]:
            new_y -= self.speed_y

        if keys[K_DOWN]:
            new_y += self.speed_y

        # Check collision with each wall for new position
        temp_rect = self.rect.copy()
        temp_rect.x = new_x
        temp_rect.y = new_y

        collide = False
        for wall in walls_group:
            if temp_rect.colliderect(wall.rect):
                offset_x = wall.rect.x - temp_rect.x
                offset_y = wall.rect.y - temp_rect.y
                if self.mask.overlap(wall.mask, (offset_x, offset_y)):
                    collide = True
                    break

        if not collide:
            self.rect.x = new_x
            self.rect.y = new_y

        if keys[K_SPACE]:
            self.fire()

# Class: Bullet
class Bullet(GameSprite):
    def __init__(self, image, x, y, w, h, speed_x, speed_y):
        super().__init__(image, x, y, w, h)
        self.speed_x = speed_x
        self.speed_y = speed_y

    # Move bullets
    def update(self):
        self.rect.x += self.speed_x
        # Remove bullets when they collide with walls or enemies
        sprite.groupcollide(bullets, walls_group, True, False)
        sprite.groupcollide(bullets, enemies, True, True)
        for bullet in bullets:
            if not bullet.rect.colliderect(window.get_rect()):
                bullet.kill()

# Class: Enemy
class Enemy(GameSprite):
    def __init__(self, image, x, y, w, h, speed_x, speed_y, point1, point2):
        super().__init__(image, x, y, w, h)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.point1 = point1
        self.point2 = point2
        self.current_target = point1

    # Move enemy between two points
    def update(self):
        if self.rect.x == self.current_target[0] and self.rect.y == self.current_target[1]:
            self.current_target = self.point1 if self.current_target == self.point2 else self.point2

        dx = self.current_target[0] - self.rect.x
        dy = self.current_target[1] - self.rect.y
        distance = sqrt(dx**2 + dy**2)

        if distance != 0:
            dx /= distance
            dy /= distance

        self.rect.x += dx * self.speed_x
        self.rect.y += dy * self.speed_y

# Create groups
bullets = sprite.Group()
walls_group = sprite.Group()
enemies = sprite.Group()

# Define walls
walls = [
    # Outer walls
    GameSprite(wall_image, 50, 550, 700, 10),  # Bottom
    GameSprite(wall_image, 50, 50, 700, 10),   # Top
    GameSprite(wall_image, 750, 50, 10, 510),  # Right
    GameSprite(wall_image, 50, 50, 10, 500),   # Left
    GameSprite(wall_image, 400, 150, 10, 400),
    GameSprite(wall_image, 400, 250, 200, 10),
    GameSprite(wall_image, 200, 250, 10, 300),
    GameSprite(wall_image, 600, 250, 10, 200),
]

# Add walls to the walls group
for wall in walls:
    walls_group.add(wall)

# Initialize game objects
def start():
    global player
    global enemies
    global FIVANSKIE_SVITKY
    global start_time
    FIVANSKIE_SVITKY = GameSprite(FIVANSKIE_SVITKY_image, 100, 450, 70, 50)
    player = Player(player_image, 500, 400, 55, 85, 5, 5)
    enemies.empty()  # Clear existing enemies
    # Define enemy movement points
    enemy1 = Enemy(enemy_NOSY_image, 290, 500, 40, 60, 2, 2, (290, 500), (190, 60))
    enemy2 = Enemy(enemy_MUMMY_image, 500, 90, 80, 120, 2, 2, (500, 90), (400, 90))
    enemies.add(enemy1, enemy2)
    start_time = time.get_ticks() // 1000  # Reset start time

def game_over():
    window.blit(blur_background_image, (0, 0))
    elapsed_time = (time.get_ticks() // 1000) - start_time
    text1 = font_style.render("Game Over", True, (255, 0, 0))
    text2 = font_style.render(f"Time: {elapsed_time}s", True, (255, 255, 255))
    text3 = font_style.render("Press 'a' to play again", True, (255, 255, 255))

    text_rect1 = text1.get_rect(center=(400, 240))
    text_rect2 = text2.get_rect(center=(400, 320))
    text_rect3 = text3.get_rect(center=(400, 400))
    
    window.blit(text1, text_rect1)
    window.blit(text2, text_rect2)
    window.blit(text3, text_rect3)
    death_effect.play()
    display.update()

def game_win():
    window.blit(blur_background_image, (0, 0))
    elapsed_time = (time.get_ticks() // 1000) - start_time
    text1 = font_style.render("You Won", True, (255, 215, 0))
    text2 = font_style.render(f"Time: {elapsed_time}s", True, (255, 255, 255))
    text3 = font_style.render("Press 'a' to play again", True, (255, 255, 255))

    text_rect1 = text1.get_rect(center=(400, 240))
    text_rect2 = text2.get_rect(center=(400, 320))
    text_rect3 = text3.get_rect(center=(400, 400))
    
    window.blit(text1, text_rect1)
    window.blit(text2, text_rect2)
    window.blit(text3, text_rect3)
    win_sound.play()
    display.update()

# Prepare for game loop
start()
game = True
finish = False
font_style = font.Font("Arabic-Cyr-(kerning-fixed).ttf", 60)
font_small = font.Font("Arabic-Cyr-(kerning-fixed).ttf", 30)

# Game loop
while game:
    for e in event.get():
        if e.type == QUIT:
            game = False
        elif e.type == KEYDOWN and e.key == K_a and finish:
            finish = False
            start()

    if finish == False:
        window.blit(background_image, (0, 0))

        # Draw and update sprites
        walls_group.draw(window)
        bullets.draw(window)
        enemies.draw(window)
        player.draw()
        FIVANSKIE_SVITKY.draw()
        enemies.update()
        player.update()
        bullets.update()

        # Check for collisions between player and enemies
        for enemy in enemies:
            offset = (player.rect.x - enemy.rect.x, player.rect.y - enemy.rect.y)
            if player.mask.overlap(enemy.mask, offset):
                finish = True
                game_over()

        offset2 = (player.rect.x - FIVANSKIE_SVITKY.rect.x, player.rect.y - FIVANSKIE_SVITKY.rect.y)
        if player.mask.overlap(FIVANSKIE_SVITKY.mask, offset2):
            finish = True
            game_win()

        # Display elapsed time
        elapsed_time = (time.get_ticks() // 1000) - start_time
        time_text = font_small.render(f"Time: {elapsed_time}s", True, (255, 255, 255))
        window.blit(time_text, (10, 10))
        
    display.update()
    time.delay(50)

# Quit Pygame
quit()
