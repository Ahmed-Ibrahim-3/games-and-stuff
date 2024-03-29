from dis import Instruction
from os import stat_result
import pygame
import random
import time
import os.path

# Define some constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 900
FPS = 60

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

CYAN = (0, 255,255)
GRAY = (100, 100, 100)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
#PURPLE = (150, 0, 255)
YELLOW = (255, 255, 0)
ORANGE = (255, 100, 0)

class Player(pygame.sprite.Sprite):
    # Sprite class for the player
    def __init__(self, image_us, image_s):
        pygame.sprite.Sprite.__init__(self)
        self.image_normal = image_us
        self.image_shielded = image_s
        self.image = self.image_normal
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.bottom = SCREEN_HEIGHT - 50
        self.shielded = False

    def update(self):
        self.speedx = 0
        # If left or right key is pressed, move left or right
        pressed_key = pygame.key.get_pressed()
        if pressed_key[pygame.K_LEFT]: 
            self.speedx = -5
        if pressed_key[pygame.K_RIGHT]:
            self.speedx = 5
        self.rect.x += self.speedx

        # No further move if off screen
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        
    def shield(self):
        self.shielded = True
        x_pos = self.rect.centerx
        self.image = self.image_shielded
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x_pos
        self.rect.bottom = SCREEN_HEIGHT - 50
    def unshield(self):
        self.shielded = False
        x_pos = self.rect.centerx
        self.image = self.image_normal
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.rect.centerx = x_pos
        self.rect.bottom = SCREEN_HEIGHT - 50

class Mob(pygame.sprite.Sprite):
    # Sprite class for the mobs
    def __init__(self, x, y, speed, health, mob_self_img):
        pygame.sprite.Sprite.__init__(self)
        self.image = mob_self_img
        self.worth = 1
        self.stats = (speed, health)
        if self.stats == (1,2):
            self.worth = 2
        elif self.stats == (2,1):
            self.worth = 1
        elif self.stats == (4,1):
            self.worth = 2
        elif self.stats == (1, 150):
            self.worth = 50
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = speed
        self.counter = 0
        self.mobhealth = health
        
    def update(self):
        if self.counter % 20 == 0: #every 20 loops
            self.rect.y += self.speedy
        if self.counter == 0:
            self.rect.x += 50
        if self.counter == 1000:
            self.rect.x -= 50
        self.counter += 1
        if self.counter == 2000:
            self.counter = 0


class Bullet(pygame.sprite.Sprite):
    # Sprite class for the bullet
    def __init__(self, x, y, powerup, bullet_image):
        pygame.sprite.Sprite.__init__(self)
        self.powerup = powerup
        self.image = bullet_image
        if self.powerup == "BulletWidth":
            self.bullethealth = 3 # High chance of getting 3 mobs, not much chance of getting 0 mobs
        elif self.powerup == 'BulletPiercing':
            self.bullethealth = 5 # Most of time gets 5 mobs, but higher chance of getting 0 mobs
        elif self.powerup == None or powerup == 'BulletBomb':
            self.bullethealth = 1 # Bomb: about equal chance of 2, 3, or 4 mobs, rarely 0, 1, 5, or 6 mobs
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -7
        self.bpowerup = powerup

    def update(self):
        self.rect.y += self.speedy
        # if a bullet run off screen, remove it
        if self.rect.bottom < 0:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, shield_pu_image, bullet_wide_pu_image, bullet_piercing_pu_image, bullet_bomb_pu_image, score_pu_image):
        pygame.sprite.Sprite.__init__(self)
        
        self.include_shield = True
        self.shield_image = shield_pu_image
        self.bullet_wide_image = bullet_wide_pu_image
        self.bullet_piercing_image = bullet_piercing_pu_image
        self.bullet_bomb_image = bullet_bomb_pu_image
        self.score_image = score_pu_image
        self.powerups = {'BulletWidth':bullet_wide_pu_image, 'BulletPiercing':bullet_piercing_pu_image, 'BulletBomb': bullet_bomb_pu_image, 'Score':score_pu_image}
        
        if self.include_shield:
            self.powerups['Shield'] = self.shield_image
            
        self.powerup = random.choice(list(self.powerups))
        self.image = self.powerups[self.powerup]
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randint(100, SCREEN_WIDTH - 100)
        self.rect.centery = random.randint(500, SCREEN_HEIGHT - 200)
        self.time = 0

    
    def return_power(self):
        return self.powerup

    def randomize(self):
        self.powerups = {'BulletWidth':self.bullet_wide_image, 'BulletPiercing':self.bullet_piercing_image, 'BulletBomb':self.bullet_bomb_image, 'Score':self.score_image}
        if self.include_shield:
            self.powerups['Shield'] = self.shield_image
        elif 'Shield' in self.powerups.keys():
            del self.powerups['Shield']
            
        self.powerup = random.choice(list(self.powerups))
        self.image = self.powerups[self.powerup]
        self.rect = self.image.get_rect()
        self.rect.centerx = random.randint(100, SCREEN_WIDTH - 100)
        self.rect.centery = random.randint(500, SCREEN_HEIGHT - 200)
        self.time = 0

    def update(self):
        self.time += 1
        if self.time == 10000:
            self.randomize()

class Button():
    def __init__(self, screen, msg,font):
        self.screen = screen
        self.screen_rect = screen.get_rect()

        self.width, self.height = 200, 50           # button size
        self.button_color = GREEN                   # button color
        self.text_color = WHITE                     # text color
        self.font = pygame.font.SysFont(None, 48)   # use default font

        # Build the button's rect object and center it on the screen
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.centerx = self.screen_rect.centerx
        self.rect.centery = self.screen_rect.centery + 175

        self.prep_msg(msg)      # Prep the text message on the button

    def prep_msg(self, msg):
        """Turn msg into a rendered image and center text on the button."""
        self.msg_image = self.font.render(msg, True, self.text_color, self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center
    
    def draw_button(self):
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)

class Game():
    
    def __init__(self, screen, screen_height, screen_width):
        
        instructions = '''space invaders clone
        Arrow keys to move.
        Space to shoot.
        Powerup guide: 
            Orange powerups makes your next bullet pierce. 
            Yellow powerups makes your next bullet big. 
            Black powerups makes your next bullet explode. 
            Grey powerups gives you a shield. 
            Cyan powerups gives you 5 points. 
        Mob guide:
            Green mobs (1 pt) are normal. 
            Purple mobs (2 pts) have more health. 
            Blue mobs (2 pts) are faster. '''
        
        font = pygame.font.SysFont('Arial', 64)
    
        def blit_text(surface, text, pos, font, color=pygame.Color('black')):  
            words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
            space = 1  # The width of a space.
            max_width, max_height = surface.get_size()
            x, y = pos
            for line in words:
                for word in line:
                    word_surface = font.render(word, 0, color)
                    word_width, word_height = word_surface.get_size()
                    if x + word_width >= max_width:
                        x = pos[0]  # Reset the x.
                        y += word_height  # Start on new row.
                    surface.blit(word_surface, (x, y))
                    x += word_width + space
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
        
        self.dir = os.path.dirname(__file__)
        self.display_text(screen, blit_text(screen,instructions,(200,200),font),30,WHITE, 200,200 )
        self.display_text(screen, "Enter your username in the terminal.", 50, WHITE, 600, 500)
        pygame.display.flip()
        self.username = input("Enter your username for saving.")

        self.bg_image = self.image('space.png', screen_width, screen_height)  
        self.bg_rect = self.bg_image.get_rect()
        # the player image
        self.player_unshielded_image = self.image('player.png', 75, 75)
        self.player_shielded_image = self.image('player_shielded.png', 75, 75)
        # the mob image
        self.mob_green_image = self.image('ufo_normal.png', 36, 36)
        self.mob_blue_image = self.image('ufo_speed.png', 36, 36)
        self.mob_purple_image = self.image('ufo_tank.png', 50, 50)
        self.mob_gray_image = self.image('ufo_boss.png', 150, 150)
        # the bullet image
        self.laser_red = self.image('laser.png', 20, 50)
        self.laser_yellow = self.image('laser_yellow.png', 60, 100)
        self.laser_orange = self.image('laser_orange.png', 10, 100)
        self.laser_grey = self.image('laser_grey.png', 30, 50)
        self.bullet_name_img_dict = {None:self.laser_red, 'BulletWidth':self.laser_yellow, 'BulletPiercing':self.laser_orange, 'BulletBomb':self.laser_grey}
        # the powerup images
        self.powerup_bullet_wide_image = self.image('powerup_bullet_wide.png', 30, 30)
        self.powerup_bullet_piercing_image = self.image('powerup_bullet_piercing.png', 30, 30)
        self.powerup_bullet_bomb_image = self.image('powerup_bomb.png', 30,30)
        self.powerup_shield_image = self.image('powerup_shield.png', 30, 30)
        self.powerup_score_image = self.image('powerup_score.png', 30, 30)

        self.high_score = 0

        self.shooting_sound = self.sound('shooting.wav')
        self.explosion_sound = self.sound('explosion.wav')

        self.reset()
        
    def reset(self):
    
        self.mNorm = (2, 1, self.mob_green_image)
        self.mTank = (1, 2, self.mob_purple_image)
        self.mFast = (4, 1, self.mob_blue_image)
        self.mBoss = (1, 150, self.mob_gray_image)

        # Create sprite groups in the game
        self.all_sprites = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        self.bullets = pygame.sprite.Group()
        self.powerups = pygame.sprite.Group()

        self.game_active = False
        self.score = 0
        self.bullet_power_up = None
        self.MAX_LEVEL = 7
        self.level = 0 
        self.level_text_timer = 0
        self.max_bullets = 3
        self.bullets_num = self.max_bullets
        self.bullet_reload_timer = 0
        self.bullet_text_color = WHITE
        self.game_played = False
        # Set up pygame and create screen

        # Create game clock that manage how fast the screen updates
        self.clock = pygame.time.Clock()
        self.clock.tick(FPS)

        # Create a player
        self.player = Player(self.player_unshielded_image, self.player_shielded_image)
        self.all_sprites.add(self.player)

        for x in range(2):
            powerup = PowerUp(self.powerup_shield_image, self.powerup_bullet_wide_image, self.powerup_bullet_piercing_image, self.powerup_bullet_bomb_image, self.powerup_score_image)
            self.all_sprites.add(powerup)
            self.powerups.add(powerup)

        # Create 2 powerups
    
    def image(self, image_name, width, height):
        img_dir = os.path.join(self.dir, 'images')
        image =  pygame.image.load(os.path.join(img_dir, image_name)).convert()
        scaled_image = pygame.transform.scale(image, (width, height))
        return scaled_image

    def sound(self, sound_name):
        sound_dir = os.path.join(self.dir, 'sounds')
        return pygame.mixer.Sound(os.path.join(sound_dir, sound_name))

    def create_mobs(self, width, height, OffsetX, OffsetY, DistDiff, mob_info):
        speed = mob_info[0]
        health = mob_info[1]
        mob_img = mob_info[2]
        for x in range(width):
            for y in range(height):
                m = Mob(OffsetX + x * DistDiff, OffsetY + y * DistDiff, speed, health, mob_img)
                self.mobs.add(m)
                self.all_sprites.add(m)
    
    def display_text(self, surf, text, size, color, x, y):
        font = pygame.font.SysFont("Arial", size)      
        text_surface = font.render(text, True, color) 
        text_rect = text_surface.get_rect()           
        text_rect.midtop = (x, y)
        surf.blit(text_surface, text_rect)

    def print_instructions(self):
        print('''space invaders clone
    Arrow keys to move.
    Space to shoot.
    Powerup guide: 
        Orange powerups makes your next bullet pierce. 
        Yellow powerups makes your next bullet big. 
        Black powerups makes your next bullet explode. 
        Grey powerups gives you a shield. 
        Cyan powerups gives you 5 points. 
    Mob guide:
        Green mobs (1 pt) are normal. 
        Purple mobs (2 pts) have more health. 
        Blue mobs (2 pts) are faster. ''')

    def get_events(self, button):
        for event in pygame.event.get():
            # If the close button is clicked, quit running
            if event.type == pygame.QUIT:
                with open(os.path.join(self.dir, 'high_scores.txt'), 'a+') as score_file:
                    #scores = score_file.readlines()
                    #score_dic = dict()
                    #for score in scores:
                    #    info = score.split(',')
                    #    score = info[1]
                    score_file.write(self.username + "," + str(self.high_score) + "," + str(self.level) + "\n")
                    # Sort scores from top to bottom TO_DO
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and self.bullets_num > 0:
                    img = self.bullet_name_img_dict[self.bullet_power_up]
                    bullet = Bullet(self.player.rect.centerx, self.player.rect.top, self.bullet_power_up, img)
                    self.bullet_power_up = None
                    self.all_sprites.add(bullet)
                    self.bullets.add(bullet)
                    self.bullets_num -= 1
                    self.shooting_sound.play()
                else:
                    pass
                    # play beep / no bullets sound TO_DO
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.check_play_button(button, mouse_x, mouse_y)
        return True
    
    def check_play_button(self, button, x, y):
        clicked = button.rect.collidepoint(x, y)
        if clicked and not self.game_active:
            self.all_sprites.empty()
            self.mobs.empty()
            self.bullets.empty()

            self.reset()
            self.game_active = True
            pygame.mouse.set_visible(False)
    
    def run(self):
        # Update sprites
        self.all_sprites.update()

        # Update levels
        if len(self.mobs) == 0:
            self.bullets.empty()
            self.level += 1
            self.level_text_timer = 0
            if self.level == 1:
                self.create_mobs(9, 3, 400, 40, 50, self.mNorm)
                self.game_played = True
            elif self.level == 2:
                self.create_mobs(11, 4, 350, 40, 50, self.mNorm)
                self.create_mobs(15, 2, 250, -80, 50, self.mNorm)
            elif self.level == 3:
                self.create_mobs(11, 5, 350, 40, 50, self.mNorm)
                self.create_mobs(15, 3, 250, -120, 50, self.mNorm)
                self.create_mobs(15, 2, 250, -100, 50, self.mFast)
                self.max_bullets = 4
            elif self.level == 4:
                self.create_mobs(11, 5, 350, 40, 50, self.mNorm)
                self.create_mobs(15, 4, 250, -150, 50, self.mNorm)
                self.create_mobs(15, 3, 250, -130, 50, self.mFast)
                self.create_mobs(15, 4, 250, -140, 60, self.mTank)
            elif self.level == 5:
                self.create_mobs(11, 5, 350, 40, 50, self.mNorm)   
                self.create_mobs(15, 5, 250, -240, 50, self.mNorm)
                self.create_mobs(15, 5, 175, -300, 60, self.mTank)
                self.create_mobs(15, 5, 250, -350, 50, self.mFast)
                self.create_mobs(1, 1, 525, -400, 0, self.mBoss)
                self.max_bullets = 5
            elif self.level == 6:
                self.create_mobs(2, 1, 525, 0, 0, self.mBoss)
            elif self.level == 7:
                self.game_active = False
            self.bullets_num = self.max_bullets

        # If a bullet hits the player, remove shield or end game
        for mob in self.mobs:
            hits = pygame.sprite.collide_rect(self.player, mob)
            if hits:
                mob.kill()
                if self.player.shielded:
                    #global explosion_sound
                    self.explosion_sound.play()
                    self.player.unshield()
                    self.score += mob.worth

                    if self.score > self.high_score:
                            self.high_score = self.score
                else:
                    self.game_active = False
            if mob.rect.bottom > SCREEN_HEIGHT:
                self.game_active = False
            # if mob hits bullet subtract from bullethealth and mobhealth
            for bullet in self.bullets:
                bullet_hits = pygame.sprite.collide_rect(bullet, mob)
                if bullet_hits:
                    bullethealth_decrease = mob.mobhealth
                    mob.mobhealth -= bullet.bullethealth
                    bullet.bullethealth -= bullethealth_decrease

                    if bullet.bullethealth <= 0:
                        bullet.kill()
                        # if bomb explode all nearby mobs
                        if bullet.powerup == 'BulletBomb':
                            self.explosion_sound.play()
                            for mob in self.mobs:
                                xdist = mob.rect.centerx - bullet.rect.centerx
                                ydist = mob.rect.centery - bullet.rect.centery
                                if xdist < 60 and xdist > -60 and ydist < 25 and ydist > -100:
                                    mob.mobhealth -= 1
                                    #self.score += mob.worth
                                    if self.score > self.high_score:
                                        self.high_score = self.score
            for mob in self.mobs:
                    # mobs dying
                if mob.mobhealth <= 0:
                    mob.kill()
                    self.explosion_sound.play()
                    self.score += mob.worth
                    if self.score > self.high_score:
                        self.high_score = self.score
        
        for pu in self.powerups:
            
            #print((not self.player.shielded, pu.include_shield))
            hits_pu = pygame.sprite.spritecollide(pu, self.bullets, False, False)
            if hits_pu:
                if pu.powerup == 'Shield':
                    self.player.shield()
                elif 'Bullet' in pu.powerup:
                    self.bullet_power_up = pu.powerup
                    #(print(bullet_power_up)
                elif pu.powerup == 'Score':
                    self.score += 5
                    if self.score > self.high_score:
                        self.high_score = self.score
                pu.include_shield = not self.player.shielded
                pu.randomize()

        if self.bullets_num < self.max_bullets:
            self.bullet_reload_timer += 1
            if self.bullet_reload_timer >= 50:
                self.bullets_num += 1
                # make reload sound TO_DO
                self.bullet_reload_timer = 0
        if self.level >= self.MAX_LEVEL:
            self.game_active = False

    def display(self, screen, button):
        # Draw background and all the sprites
        #screen.blit(bg_image, (0,0))
        screen.fill(BLACK) # because images have black background, looks better

        if not self.game_active:
            if self.game_played:
                self.end_game(screen)
            button.draw_button()
            pygame.mouse.set_visible(True)
        else:
            self.display_text(screen, "Score: " + str(self.score), 25, CYAN, 100, 100)
            self.display_text(screen, "High Score: " + str(self.high_score), 25, BLUE, 100, 150)
            self.display_text(screen, "Level: " + str(self.level), 25, WHITE, 100, 200)
            if self.bullet_power_up == None:
                self.bullet_text_color = WHITE
            elif self.bullet_power_up == 'BulletWidth':
                self.bullet_text_color = YELLOW
            elif self.bullet_power_up == 'BulletPiercing':
                self.bullet_text_color = ORANGE
            elif self.bullet_power_up == 'BulletBomb':
                self.bullet_text_color = GRAY
            self.display_text(screen, str(self.bullets_num) + " |" + str(self.bullet_reload_timer), 25, self.bullet_text_color, self.player.rect.centerx, self.player.rect.centery - 75)
            self.all_sprites.draw(screen)

            if self.level_text_timer < 500:
                self.display_text(screen, 'Level ' + str(self.level), 25, WHITE, 600, 600)
                self.level_text_timer += 1

        # Flip the display after drawing is done
        pygame.display.flip()

    def end_game(self, screen):
        #print("Highest Level Reached: " + str(self.level) + "/" + str(self.MAX_LEVEL))
        #screen.blit(bg_image, (0,0))
        screen.fill(BLACK)
        self.display_text(screen, "GAME OVER", 50, RED, 600, 475)
        self.display_text(screen, "Final Score: " + str(self.score), 25, CYAN, 600, 550)
        self.display_text(screen, "High Score: " + str(self.high_score), 25, BLUE, 600, 575)
        self.display_text(screen, "Highest Level Reached: " + str(self.level) + "/" + str(self.MAX_LEVEL), 25, WHITE, 600, 600)
        # Draw top 5 or 10 high score screen TO_DO

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Space invaders clone")

    clock = pygame.time.Clock()
    play_button= Button(screen, "Play",'Arial')
    game = Game(screen, SCREEN_WIDTH, SCREEN_HEIGHT)
    game.print_instructions()
    # Main game loop
    running = True

    while running:
        running = game.get_events(play_button)
        if game.game_active:
            game.run()
        game.display(screen, play_button)
        clock.tick(FPS)
    

main()