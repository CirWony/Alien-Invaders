import pygame
import pygame.font
import sys
import wave
from random import choice
import random
from pygame import *
from time import sleep
from pygame.sprite import Sprite
from pygame.sprite import Group
from operator import itemgetter

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
GRAY = (128, 128, 128)

IMAGE_PATH = 'images/'
SOUND_PATH = 'sounds/'

# Font
FONT = 'fonts/FLORIAN.otf'

# Sounds
soundtrack_slow = SOUND_PATH + 'soundtrack_slow.wav'
soundtrack_medium = SOUND_PATH + 'soundtrack_medium.wav'
soundtrack_fast = SOUND_PATH + 'soundtrack_fast.wav'

slow_wav = wave.open(soundtrack_slow)
slow_freq = slow_wav.getframerate()

medium_wav = wave.open(soundtrack_medium)
medium_freq = medium_wav.getframerate()

fast_wav = wave.open(soundtrack_fast)
fast_freq = fast_wav.getframerate()

# Images
SCREEN = display.set_mode((800, 700))
IMG_NAMES = ['Ship_1', 'Special_1', 'Alien1_1', 'Alien1_2', 'Alien2_1', 'Alien2_2', 'Alien3_1', 'Alien3_2', 'Explosion',
             'Explosion1', 'Ship_2', 'Ship_3', 'Ship_4', 'Ship_5']
IMAGES = {name: image.load(IMAGE_PATH + '{}.png'.format(name)).convert_alpha() for name in IMG_NAMES}
Alien1 = 'images/Alien1_1.png', 'images/Alien1_2.png'
Alien2 = 'images/Alien2_1.png', 'images/Alien2_2.png'
Alien3 = 'images/Alien3_1.png', 'images/Alien3_2.png'

ENEMY_DEFAULT_POSITION = 65

# Clock Speed
clock = pygame.time.Clock()


class Text(object):
    """Rendering text and fonts."""
    def __init__(self, text_font, size, message, colors, x_pos, y_pos):
        self.font = font.Font(text_font, size)
        self.surface = self.font.render(message, True, colors)
        self.rect = self.surface.get_rect(topleft=(x_pos, y_pos))

    def draw(self, surface):
        surface.blit(self.surface, self.rect)


class Invaders(object):
    """Run the game."""
    def __init__(self):
        # Initialize game and create a screen object.
        pygame.init()
        # Test
        mixer.pre_init(44100, -16, 1, 4096)
        self.clock = time.Clock()
        self.caption = display.set_caption('Space Invaders')
        self.screen = SCREEN

        self.background = image.load('images/background.jpg')
        self.background = pygame.transform.scale(self.background, (800, 700))
        self.startGame = False
        self.mainScreen = True
        self.highScore = False
        self.gameOver = False

        self.enemyPosition = ENEMY_DEFAULT_POSITION
        self.titleText = Text(FONT, 50, 'Space Invaders', WHITE, 165, 155)
        self.titleText2 = Text(FONT, 25, 'Press "P" key to Play', WHITE, 250, 225)
        self.gameOverText = Text(FONT, 50, 'Game Over', WHITE, 250, 270)
        self.nextRoundText = Text(FONT, 50, 'Next Round', WHITE, 240, 270)
        self.enemy1Text = Text(FONT, 25, '   =  30 pts', GREEN, 370, 270)
        self.enemy2Text = Text(FONT, 25, '   =  20 pts', YELLOW, 370, 320)
        self.enemy3Text = Text(FONT, 25, '   =  10 pts', PURPLE, 370, 370)
        self.enemy4Text = Text(FONT, 25, '   =  50-200 pts', RED, 370, 420)
        self.titleText3 = Text(FONT, 25, 'Press "H" to see High Scores', WHITE, 200, 480)
        self.hiText = Text(FONT, 50, 'High Scores', WHITE, 165, 155)
        self.hiText1 = Text(FONT, 25, 'Press "Esc" to go back', WHITE, 165, 545)

        self.explosionsGroup = Group()
        self.shipExplosionGroup = Group()

        # Initialize settings class
        self.ai_settings = Settings()
        # Make a ship
        self.ship = Ship(self.ai_settings, self.screen)
        # Make a group for bullets
        self.bullets = Group()
        self.greenBullet = Group()
        # Make aliens appear
        self.alien = Group()
        # Game Stats
        self.stats = GameStats(self.ai_settings)
        # Scoreboard
        self.sb = Scoreboard(self.ai_settings, self.screen, self.stats)

        # Make Python happy format
        self.noteIndex = None
        self.sounds = None
        self.create_audio()

        self.alien1 = None
        self.alien2 = None
        self.alien3 = None
        self.alien4 = None
        self.game_time = None
        self.score = 0

        self.allBunkers = None
        self.specialAlien = None
        self.specialGroup = None
        self.timer = None
        self.allSprites = None
        self.shooter = None
        self.enemyBulletTimer = None
        self.reset(0)

    # Initialize game
    def reset(self, score):
        # self.ai_settings = Settings()
        # self.ship = Ship(self.ai_settings, self.screen)
        self.explosionsGroup = Group()
        # self.shipExplosionGroup = Group()
        self.bullets = Group()
        self.alien = Group()
        # self.stats = GameStats(self.ai_settings)
        self.sb = Scoreboard(self.ai_settings, self.screen, self.stats)
        self.allBunkers = Group(self.create_bunkers(0), self.create_bunkers(1), self.create_bunkers(2),
                                self.create_bunkers(3))
        self.specialAlien = Special()
        self.specialGroup = Group(self.specialAlien)
        self.greenBullet = Group()
        self.allSprites = Group(self.ship, self.allBunkers)
        self.timer = time.get_ticks()
        self.enemyBulletTimer = time.get_ticks()
        self.score = score
        self.create_audio()

    def run_game(self):
        pygame.display.set_caption("Alien Invaders")

        # Create the fleet
        self.create_fleet(self.ai_settings, self.screen, self.alien)

        # Menu soundtrack
        self.background_noise(slow_freq, soundtrack_slow)
        pygame.mixer.music.play()

        # Start the main loop for the game.
        while True:
            clock.tick(60)
            # Main Start Menu
            if self.mainScreen:
                # Title Texts
                self.screen.blit(self.background, (0, 0))
                self.titleText.draw(self.screen)
                self.titleText2.draw(self.screen)
                self.enemy1Text.draw(self.screen)
                self.enemy2Text.draw(self.screen)
                self.enemy3Text.draw(self.screen)
                self.enemy4Text.draw(self.screen)
                self.titleText3.draw(self.screen)
                self.create_main_menu()
                pygame.display.update()
                for events in pygame.event.get():
                    if events.type == pygame.QUIT:
                        sys.exit()
                    if pygame.key.get_pressed()[pygame.K_h]:
                        print('Accessing High Score...')
                        self.mainScreen = False
                        self.highScore = True
                    if pygame.key.get_pressed()[pygame.K_p]:
                        print('Playing...')
                        self.reset(0)
                        self.startGame = True
                        self.mainScreen = False

            # High Score Menu
            elif self.highScore:
                scores = []
                x = 0
                with open('highscores.txt') as f:
                    for line in f:
                        name, score = line.split(',')
                        score = int(score)
                        scores.append((name, score))
                scores = sorted(scores, key=itemgetter(1), reverse=True)[:10]
                for name, score in scores:
                    if name == 'You':
                        Text(FONT, 15, name + ': ' + str(score), RED, 165, 230 + (30 * x)).draw(self.screen)
                    else:
                        Text(FONT, 15, name + ': ' + str(score), YELLOW, 165, 230 + (30 * x)).draw(self.screen)
                    pygame.display.update()
                    x += 1

                self.screen.blit(self.background, (0, 0))
                self.hiText.draw(self.screen)
                self.hiText1.draw(self.screen)
                high_score_text2 = Text(FONT, 15, 'Your score: ' + str(self.score), YELLOW, 165, 130)
                high_score_text2.draw(self.screen)
                pygame.display.update()
                for events in pygame.event.get():
                    if events.type == pygame.QUIT:
                        sys.exit()
                    if pygame.key.get_pressed()[pygame.K_ESCAPE]:
                        self.mainScreen = True
                        self.highScore = False

            # Game running loop
            elif self.startGame:
                current_time = time.get_ticks()
                self.check_events(self.ai_settings, self.screen, self.ship, self.bullets)
                self.update_bullets(self.ai_settings, self.screen, self.stats, self.sb, self.ship, self.alien,
                                    self.specialGroup, self.bullets)
                self.update_aliens(self.ai_settings, self.screen, self.stats, self.sb, self.ship, self.alien,
                                   self.bullets)
                self.update_screen(self.screen, self.ship, self.alien, self.bullets)
                self.ship.update()
                if self.alien:
                    self.who_is_shooting()
                    self.enemy_fire_bullet(self.shooter.rect)
                self.allSprites.draw(self.screen)
                self.specialGroup.update(current_time)
                self.explosionsGroup.update(current_time)
                self.shipExplosionGroup.update(current_time)
                pygame.display.update()

    @staticmethod
    def background_noise(freq, soundtrack):
        pygame.mixer.init(freq)
        pygame.mixer.music.load(soundtrack)

    @staticmethod
    def background_noise_quit():
        pygame.mixer.quit()

    def current_high_score(self):
        return self.score

    @staticmethod
    def high_score_load():
        scores = []
        x = 0
        with open('highscores.txt') as f:
            for line in f:
                name, score = line.split(',')
                score = int(score)
                scores.append((name, score))
        scores = sorted(scores, key=itemgetter(1), reverse=True)[:10]
        for name, score in scores:
            high_score_top_10 = Text(FONT, 15, name + ': ' + str(score), YELLOW, 165, 230 + (30 * x))
            x += 1
            return high_score_top_10

    def create_main_menu(self):
        self.alien1 = IMAGES['Alien1_1']
        self.alien1 = transform.scale(self.alien1, (40, 40))
        self.alien2 = IMAGES['Alien2_1']
        self.alien2 = transform.scale(self.alien2, (40, 40))
        self.alien3 = IMAGES['Alien3_1']
        self.alien3 = transform.scale(self.alien3, (40, 40))
        self.alien4 = IMAGES['Special_1']
        self.alien4 = transform.scale(self.alien4, (80, 40))
        self.screen.blit(self.alien1, (318, 270))
        self.screen.blit(self.alien2, (318, 320))
        self.screen.blit(self.alien3, (318, 370))
        self.screen.blit(self.alien4, (299, 420))

    @staticmethod
    def create_bunkers(number):
        bunker_group = Group()
        for row in range(4):
            for column in range(9):
                bunker = Bunker(10, GRAY, row, column)
                bunker.rect.x = 50 + (200 * number) + (column * bunker.width)
                bunker.rect.y = 550 + (row * bunker.height)
                bunker_group.add(bunker)
        return bunker_group

    def check_events(self, ai_settings, screen, ship, bullets):
        """Respond to key presses."""
        for events in pygame.event.get():
            if events.type == pygame.QUIT:
                sys.exit()
            elif events.type == pygame.KEYDOWN:
                self.check_keydown_events(events, ai_settings, screen, ship, bullets)
            elif events.type == pygame.KEYUP:
                self.check_keyup_events(events, ship)

    def check_keydown_events(self, events, ai_settings, screen, ship, bullets):
        """Respond to key presses."""
        if events.key == pygame.K_RIGHT:
            ship.moving_right = True
        elif events.key == pygame.K_LEFT:
            ship.moving_left = True
        elif events.key == pygame.K_SPACE:
            self.fire_bullet(ai_settings, screen, ship, bullets)
        elif events.key == pygame.K_q:
            sys.exit()

    def fire_bullet(self, ai_settings, screen, ship, bullets):
        """Fire a bullet."""
        # Create a new bullet and add it to the group
        if len(bullets) < ai_settings.bullets_allowed:
            new_bullet = Bullet(ai_settings, screen, ship)
            self.greenBullet.add(new_bullet)
            self.bullets.add(self.greenBullet)
            self.allSprites.add(self.bullets)
            self.sounds['pew'].play()

    def enemy_fire_bullet(self, rect):
        """Make enemies fire."""
        if (pygame.time.get_ticks() - self.enemyBulletTimer) > 800:
            self.bullets.add(EnemyBullet(rect, RED, 1, 5))
            self.allSprites.add(self.bullets)
            self.enemyBulletTimer = time.get_ticks()

    def who_is_shooting(self):
        """Find that shooter boi."""
        column_list = []
        for enemy in self.alien:
            column_list.append(enemy.column)
        column_set = set(column_list)
        column_list = list(column_set)
        random.shuffle(column_list)
        column = column_list[0]
        row_list = []

        for enemy in self.alien:
            if enemy.column == column:
                row_list.append(enemy.row)

        for enemy in self.alien:
            if enemy.column == column and enemy.row:
                self.shooter = enemy

    @staticmethod
    def check_keyup_events(events, ship):
        """Respond to key releases."""
        if events.key == pygame.K_RIGHT:
            ship.moving_right = False
        elif events.key == pygame.K_LEFT:
            ship.moving_left = False

    def update_screen(self, screen, ship, alien, bullets):
        """Update images on the screen."""
        # Redraw the screen during each pass.
        self.screen.blit(self.background, (0, 0))
        self.allBunkers.update(self.screen)
        for bullet in bullets.sprites():
            bullet.draw_bullet()
        ship.blitme()
        alien.draw(screen)
        # Draw the score info
        self.sb.show_score()

        pygame.display.flip()

    def update_bullets(self, ai_settings, screen, stats, sb, ship, aliens, special, bullets):
        """Update position of bullets and get rid of old bullets."""
        # Update position
        bullets.update()
        self.check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, special, bullets)

        # Delete old bullets
        for bullet in bullets.copy():
            if bullet.rect.bottom <= 0:
                bullets.remove(bullet)
        self.check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, special, bullets)

    def scoring(self, row):
        scores = {0: 30,
                  1: 20,
                  2: 20,
                  3: 10,
                  4: 10,
                  5: choice([50, 100, 150, 200])}
        score = scores[row]
        self.score += score
        return score

    def check_bullet_alien_collisions(self, ai_settings, screen, stats, sb, ship, aliens, special, bullets):
        reds = (shot for shot in self.bullets if shot.color == RED)
        red_bullets = Group(reds)

        # Check for collisions
        for aliens in pygame.sprite.groupcollide(aliens, bullets, True, True).keys():
            self.sounds['invaderkilled'].play()
            Explosion(aliens, self.explosionsGroup)
            self.game_time = time.get_ticks()
            stats.score += self.scoring(aliens.row)
            sb.prep_score()
            self.check_high_score(stats, sb)

        for special in pygame.sprite.groupcollide(special, bullets, True, True):
            self.sounds['invaderkilled'].play()
            new_special = Special()
            self.specialGroup.add(new_special)
            self.game_time = time.get_ticks()
            stats.score += self.scoring(5)
            SpecialExplosion(special, self.scoring(5), self.explosionsGroup)
            sb.prep_score()
            self.check_high_score(stats, sb)

        # Enemy bullet collide with ship
        if pygame.sprite.spritecollide(ship, red_bullets, True, False):
            self.ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets)
            self.reset(self.score)

        # Bullet collide with bunker
        pygame.sprite.groupcollide(red_bullets, self.allBunkers, True, True)
        pygame.sprite.groupcollide(self.greenBullet, self.allBunkers, True, True)

        # Check if all aliens are destroyed
        if not aliens:
            # Destroy existing bullets
            bullets.empty()
            red_bullets.empty()
            ai_settings.increase_speed()
            self.create_fleet(self.ai_settings, screen, aliens)

            # Increase level
            stats.level += 1
            sb.prep_level()

            # Increase soundtrack
            if stats.level == 5:
                self.background_noise_quit()
                self.background_noise(medium_freq, soundtrack_medium)
                pygame.mixer.music.play()
            elif stats.level == 10:
                self.background_noise_quit()
                self.background_noise(fast_freq, soundtrack_fast)
                pygame.mixer.music.play()

    def create_audio(self):
        self.sounds = {}

        for sound_name in ['invaderkilled', 'pew', 'mysteryentered', 'shipexplosion']:
            self.sounds[sound_name] = mixer.Sound('sounds/' + '{}.wav'.format(sound_name))
            self.sounds[sound_name].set_volume(0.1)

        self.noteIndex = 0

    def create_fleet(self, ai_settings, screen, aliens):
        """Create a full armada."""

        # Create the rows of aliens
        for row_number in range(5):
            for alien_number in range(7):
                if row_number < 1:
                    if alien_number % 2 == 1:
                        self.create_alien(ai_settings, screen, aliens, alien_number, row_number, Alien1, 0,
                                          alien_number)
                    else:
                        self.create_alien(ai_settings, screen, aliens, alien_number, row_number, Alien1, 1,
                                          alien_number)
                elif 1 <= row_number <= 2:
                    if alien_number % 2 == 1:
                        self.create_alien(ai_settings, screen, aliens, alien_number, row_number, Alien2, 0,
                                          alien_number)
                    else:
                        self.create_alien(ai_settings, screen, aliens, alien_number, row_number, Alien2, 1,
                                          alien_number)
                elif 2 < row_number <= 4:
                    if alien_number % 2 == 1:
                        self.create_alien(ai_settings, screen, aliens, alien_number, row_number, Alien3, 0,
                                          alien_number)
                    else:
                        self.create_alien(ai_settings, screen, aliens, alien_number, row_number, Alien3, 1,
                                          alien_number)

    @staticmethod
    def get_number_aliens_x(ai_settings, alien_width):
        """Amount of aliens in a row."""
        available_space_x = ai_settings.screen_width - 2 * alien_width
        number_aliens_x = int(available_space_x / (2 * alien_width))
        return number_aliens_x

    def create_alien(self, ai_settings, screen, aliens, alien_number, row_number, images, pos, col):
        """Create an alien."""
        alien = Aliens(ai_settings, screen, images, pos, row_number, col)
        alien_width = alien.rect.width
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number + 50
        self.allSprites.add(alien)
        aliens.add(alien)

    def update_aliens(self, ai_settings, screen, stats, sb, ship, aliens, bullets):
        """Update the positions of all aliens in the fleet."""
        aliens.update()

        # Look for alien-ship collisions
        if pygame.sprite.spritecollideany(ship, aliens):
            self.ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets)
        self.check_fleet_edges(ai_settings, aliens)

        # Look for alien-bottom collisions
        self.check_aliens_bottom(ai_settings, screen, stats, sb, ship, aliens, bullets)

    def check_fleet_edges(self, ai_settings, aliens):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in aliens.sprites():
            if alien.check_edges():
                self.change_fleet_direction(ai_settings, aliens)
                break

    @staticmethod
    def change_fleet_direction(ai_settings, aliens):
        """Drop the armada!"""
        for alien in aliens.sprites():
            alien.rect.y += ai_settings.fleet_drop_speed
        ai_settings.fleet_direction *= -1

    def ship_hit(self, ai_settings, screen, stats, sb, ship, aliens, bullets):
        """Respond to ship being hit by aliens."""
        self.sounds['shipexplosion'].play()
        ShipExplosion(ship, self.shipExplosionGroup)

        for ship in pygame.sprite.spritecollide(ship, aliens, True, False):
            ShipExplosion(ship, self.shipExplosionGroup)

        if stats.ships_left > 0:
            # Decrement ship's life
            stats.ships_left -= 1
            # Update scoreboard
            sb.prep_ships()
            # Empty the list of aliens and bullets
            bullets.empty()
            aliens.empty()
            # Create a new fleet
            self.create_fleet(ai_settings, screen, aliens)
            # Pause
            sleep(0.5)
        else:
            try:
                high_score_file = open('highscores.txt', 'a')
                high_score_file.write('\n' + 'You,' + str(self.score))
                high_score_file.close()
            except IOError:
                print('Door Stuck')

            self.highScore = True
            self.mainScreen = False
            self.startGame = False

    def check_aliens_bottom(self, ai_settings, screen, stats, sb, ship, aliens, bullets):
        """Check if any alien has touched the bottom."""
        screen_rect = screen.get_rect()
        for alien in aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self.ship_hit(ai_settings, screen, stats, sb, ship, aliens, bullets)
                break
            if alien.rect.bottom >= 550:
                pygame.sprite.groupcollide(self.alien, self.allBunkers, False, True)
                break

    @staticmethod
    def check_high_score(stats, sb):
        """Check to see if there is a new high score."""
        if stats.score > stats.high_score:
            stats.high_score = stats.score
            sb.prep_high_score()


class Settings:
    """Store all settings for game."""

    def __init__(self):
        """Initialize game settings"""
        # Screen settings
        self.screen_width = 800
        self.screen_height = 700
        self.bg_color = BLACK

        # Ship settings
        self.ship_speed_factor = 5
        self.ship_limit = 3

        # Bullet settings
        self.bullet_speed_factor = 1
        self.bullet_width = 5
        self.bullet_height = 15
        self.bullets_allowed = 100
        self.bullet_color = GREEN

        # Alien settings
        self.alien_speed_factor = 1
        self.fleet_drop_speed = 5
        self.fleet_direction = 1

        # Game scale
        self.speedup_scale = 1.3
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

        # Scoring
        self.alien_points = 50

    def initialize_dynamic_settings(self):
        self.ship_speed_factor = 10
        self.bullet_speed_factor = 10
        self.alien_speed_factor = 1

        self.fleet_direction = 1

    def increase_speed(self):
        """Increase speed settings."""
        self.alien_speed_factor *= self.speedup_scale
        self.alien_points = int(self.alien_points * self.score_scale)


class Ship(Sprite):
    """Ship stuff."""

    def __init__(self, ai_settings, screen):
        """Initialize the ship and its starting position."""
        super(Ship, self).__init__()
        self.screen = screen
        self.ai_settings = ai_settings

        # Load the ship image and get its rect.
        self.image = IMAGES['Ship_1']
        self.rect = self.image.get_rect()
        self.screen_rect = screen.get_rect()

        # Start each new ship  at the bottom center.
        self.rect.centerx = self.screen_rect.centerx
        self.rect.bottom = self.screen_rect.bottom

        # Store decimal value for the ship's center
        self.center = float(self.rect.centerx)

        # Movement flags.
        self.moving_right = False
        self.moving_left = False

    def update(self):
        """Update the ship's position based on movement flags."""
        if self.moving_right and self.rect.right < self.screen_rect.right:
            self.center += self.ai_settings.ship_speed_factor
        if self.moving_left and self.rect.left > 0:
            self.center -= self.ai_settings.ship_speed_factor

        # Update rect object from self.center
        self.rect.centerx = self.center

    def center_ship(self):
        """Center the ship onto the screen."""
        self.center = self.screen_rect.centerx

    def blitme(self):
        """Draw the ship at its current location."""
        self.screen.blit(self.image, self.rect)


class EnemyBullet(Sprite):
    def __init__(self, rect, colors, vectory, speed):
        Sprite.__init__(self)
        self.width = 5
        self.height = 5
        self.color = colors
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.centerx = rect.centerx
        self.rect.top = rect.bottom
        self.name = 'bullet'
        self.vectory = vectory
        self.speed = speed
        self.oldLocation = None
        self.update()

    def update(self):
        self.oldLocation = (self.rect.x, self.rect.y)
        self.rect.y += self.vectory * self.speed

        if self.rect.bottom < 0:
            self.kill()

    def draw_bullet(self):
        """Draw the bullet to the screen."""
        pygame.draw.rect(self.image, self.color, self.rect)


class Bullet(Sprite):
    """Managing bullets."""

    def __init__(self, ai_settings, screen, ship):
        super(Bullet, self).__init__()
        self.screen = screen

        self.width = 5
        self.height = 5
        self.color = GREEN
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)

        # Create a bullet rect at (0,0) and then set correct position
        self.rect = pygame.Rect(0, 0, ai_settings.bullet_width, ai_settings.bullet_height)
        self.rect.centerx = ship.rect.centerx
        self.rect.top = ship.rect.top

        # Store the bullet's position as a decimal value
        self.y = float(self.rect.y)

        self.color = ai_settings.bullet_color
        self.speed_factor = ai_settings.bullet_speed_factor

    def update(self):
        """Move the bullet up the screen."""
        # Update the decimal position of the bullet
        self.y -= self.speed_factor
        # Update the rect position
        self.rect.y = self.y

    def draw_bullet(self):
        """Draw the bullet to the screen."""
        pygame.draw.rect(self.screen, self.color, self.rect)


class Aliens(Sprite):
    """Alien squad home base"""

    def __init__(self, ai_settings, screen, images, pos, row, column):
        super(Aliens, self).__init__()
        self.screen = screen
        self.ai_settings = ai_settings
        self.pos = pos
        self.row = row
        self.column = column
        self.timer = time.get_ticks()

        # Load the images
        self.image = pygame.image.load(images[self.pos])
        self.rect = self.image.get_rect()

        # Start each new alien near the top left of screen
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height
        self.centerx = self.rect.x / 2
        self.bottom = self.rect.bottom

        # Store the alien's position
        self.x = float(self.rect.x)

    def update(self):
        """Move the aliens left or right."""
        self.x += (self.ai_settings.alien_speed_factor * self.ai_settings.fleet_direction)
        self.rect.x = self.x

    def check_edges(self):
        """Return true if Alien is at edge of screen."""
        screen_rect = self.screen.get_rect()
        if self.rect.right >= screen_rect.right:
            return True
        elif self.rect.left <= 0:
            return True

    def blitme(self):
        """Draw aliens."""
        self.screen.blit(self.image, self.rect)


class GameStats:
    """Track statistics for game."""

    def __init__(self, ai_settings):
        self.ai_settings = ai_settings
        self.high_score = 0
        self.ships_left = self.ai_settings.ship_limit
        self.score = None
        self.level = None
        self.reset_stats()

        # Start game in an inactive state
        self.game_active = True

    def reset_stats(self):
        self.ships_left = self.ai_settings.ship_limit
        self.score = 0
        self.level = 0


class Scoreboard:
    """Scoring information."""

    def __init__(self, ai_settings, screen, stats):
        self.screen = screen
        self.screen_rect = screen.get_rect()
        self.ai_settings = ai_settings
        self.stats = stats
        self.ships = Group()

        self.level_image = None
        self.level_image_1 = None
        self.level_rect = 0
        self.high_score_image = 0
        self.high_score_rect = 0

        # Font settings
        self.text_color = GRAY
        self.font = pygame.font.SysFont(None, 48)

        # Initial score
        self.prep_score()
        self.prep_high_score()
        self.prep_level()
        self.prep_ships()
        self.score_rect = None
        self.score_image = None
        self.score_image_1 = None
        self.prep_score()

    def prep_ships(self):
        self.ships = Group()
        for ship_number in range(self.stats.ships_left):
            ship = Ship(self.ai_settings, self.screen)
            ship.rect.x = 10 + ship_number * ship.rect.width
            ship.rect.y = 10
            self.ships.add(ship)

    def prep_level(self):
        self.level_image_1 = self.font.render(str(self.stats.level), True, self.text_color, self.ai_settings.bg_color)

        # Position level below score
        self.level_rect = self.level_image_1.get_rect()
        self.level_rect.right = self.score_rect.right
        self.level_rect.top = self.score_rect.bottom + 10

        self.level_image = Text(FONT, 25, str(self.stats.level), WHITE, self.level_rect.right - 50,
                                self.level_rect.top - 15)

    @staticmethod
    def get_high_score():
            scores = []
            x = 0
            with open('highscores.txt') as f:
                for line in f:
                    name, score = line.split(',')
                    score = int(score)
                    scores.append((name, score))
            scores = sorted(scores, key=itemgetter(1), reverse=True)[:1]
            for name, score in scores:
                high_score_top_1 = score
                x += 1
                return high_score_top_1

    def prep_high_score(self):
        high_score = self.get_high_score()
        high_score_str = "{:,}".format(high_score)
        self.high_score_image = self.font.render(high_score_str, True, self.text_color, self.ai_settings.bg_color)

        # Center high score on top of screen
        self.high_score_rect = self.high_score_image.get_rect()
        self.high_score_rect.centerx = self.screen_rect.centerx
        self.high_score_rect.top = 20

    def prep_score(self):
        """Score into rendered image."""
        rounded_score = int(round(self.stats.score, -1))
        score_str = "{:,}".format(rounded_score)
        self.score_image_1 = self.font.render(score_str, True, self.text_color, self.ai_settings.bg_color)

        # Display the score at the top right
        self.score_rect = self.score_image_1.get_rect()
        self.score_rect.right = self.screen_rect.right - 20
        self.score_rect.top = 20

        self.score_image = Text(FONT, 25, score_str, WHITE, 720, 20)

    def show_score(self):
        """Draw score to the screen."""
        # Draw score
        Text(FONT, 15, 'Score: ', WHITE, 650, 25).draw(self.screen)
        self.score_image.draw(self.screen)
        # Draw high score
        Text(FONT, 15, 'High Score: ', WHITE, 352, 5).draw(self.screen)
        self.screen.blit(self.high_score_image, self.high_score_rect)
        # Draw level
        Text(FONT, 15, 'Level: ', WHITE, 652, 55).draw(self.screen)
        self.level_image.draw(self.screen)
        # Draw ships
        self.ships.draw(self.screen)


class Explosion(Sprite):
    def __init__(self, alien, *groups):
        super(Explosion, self).__init__(*groups)
        self.image = transform.scale(self.get_image(0), (40, 35))
        self.image2 = transform.scale(self.get_image(1), (50, 45))
        self.rect = self.image.get_rect(topleft=(alien.rect.x, alien.rect.y))
        self.timer = time.get_ticks()

    @staticmethod
    def get_image(number):
        if number == 0:
            return IMAGES['Explosion']
        elif number == 1:
            return IMAGES['Explosion1']

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if passed <= 100:
            game.screen.blit(self.image, self.rect)
        elif passed <= 200:
            game.screen.blit(self.image2, (self.rect.x - 6, self.rect.y - 6))
        elif passed > 400:
            self.kill()


class ShipExplosion(Sprite):
    def __init__(self, ship, *groups):
        super(ShipExplosion, self).__init__(*groups)
        self.image = transform.scale(self.get_image(0), (40, 35))
        self.image2 = transform.scale(self.get_image(1), (50, 45))
        self.image3 = transform.scale(self.get_image(2), (50, 45))
        self.image4 = transform.scale(self.get_image(3), (50, 45))
        self.rect = self.image.get_rect(topleft=(ship.rect.x - 7, ship.rect.top - 1))
        self.timer = time.get_ticks()

    @staticmethod
    def get_image(number):
        if number == 0:
            return IMAGES['Ship_2']
        elif number == 1:
            return IMAGES['Ship_3']
        elif number == 2:
            return IMAGES['Ship_4']
        elif number == 3:
            return IMAGES['Ship_5']

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if passed <= 530:
            game.screen.blit(self.image2, (self.rect.x, self.rect.y))
        elif passed <= 550:
            game.screen.blit(self.image3, (self.rect.x, self.rect.y))
        elif passed <= 570:
            game.screen.blit(self.image4, (self.rect.x, self.rect.y))
        elif passed <= 590:
            game.screen.blit(self.image4, (self.rect.x, self.rect.y))
        elif passed > 620:
            self.kill()


class SpecialExplosion(Sprite):
    def __init__(self, mystery, score, *groups):
        super(SpecialExplosion, self).__init__(*groups)
        self.text = Text(FONT, 20, str(score), WHITE, mystery.rect.x + 20, mystery.rect.y + 6)
        self.image = transform.scale(self.get_image(), (50, 45))
        self.rect = self.image.get_rect(topleft=(mystery.rect.x, mystery.rect.y))
        self.timer = time.get_ticks()

    @staticmethod
    def get_image():
        return IMAGES['Explosion']

    def update(self, current_time, *args):
        passed = current_time - self.timer
        if passed <= 200:
            self.text.draw(game.screen)
        elif passed > 400:
            self.kill()


class Bunker(Sprite):
    def __init__(self, size, colors, row, column):
        Sprite.__init__(self)
        self.height = size
        self.width = size
        self.color = colors
        self.image = Surface((self.width, self.height))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.row = row
        self.column = column

    def update(self, keys, *args):
        game.screen.blit(self.image, self.rect)


class Special(Sprite):
    def __init__(self):
        Sprite.__init__(self)
        self.image = IMAGES['Special_1']
        self.image = transform.scale(self.image, (75, 35))
        self.rect = self.image.get_rect(topleft=(-80, 45))
        self.row = 5
        self.move_time = 10000
        self.direction = 1
        self.timer = time.get_ticks()
        self.mysteryentered = mixer.Sound(SOUND_PATH + 'mysteryentered.wav')
        self.mysteryentered.set_volume(0.3)
        self.playSound = True

    def update(self, current_time, *args):
        reset_timer = False
        passed = current_time - self.timer
        if passed > self.move_time:
            if (self.rect.x < 0 or self.rect.x > 800) and self.playSound:
                self.mysteryentered.play()
                self.playSound = False
            if self.rect.x < 850 and self.direction == 1:
                self.mysteryentered.fadeout(4000)
                self.rect.x += 2
                game.screen.blit(self.image, self.rect)
            if self.rect.x > -100 and self.direction == -1:
                self.mysteryentered.fadeout(4000)
                self.rect.x -= 2
                game.screen.blit(self.image, self.rect)

        if self.rect.x > 800:
            self.playSound = True
            self.direction = -1
            reset_timer = True
        if self.rect.x < -90:
            self.playSound = True
            self.direction = 1
            reset_timer = True
        if passed > self.move_time and reset_timer:
            self.timer = current_time


if __name__ == '__main__':
    game = Invaders()
    game.run_game()
