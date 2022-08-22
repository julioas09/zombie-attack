import sys
from time import sleep
import random

import pygame

from settings import Settings
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button
from soldier import Soldier
from bullet import Bullet
from zombie import Zombie
from machinegun import Machinegun
from monster import Monster


class ZombieInvasion:
    """Overall class to manage game assets and behavior."""

    def __init__(self):
        """Initialize the game, and create game resources."""
        pygame.init()
        self.settings = Settings()

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.settings.screen_width = self.screen.get_rect().width
        self.settings.screen_height = self.screen.get_rect().height
        pygame.display.set_caption("Zombie Attack")

        # Create an instance to store game statistics,
        #   and create a scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        self.soldier = Soldier(self)
        self.bullets = pygame.sprite.Group()
        self.zombies = pygame.sprite.Group()
        self.machinegun = None
        self.weapon_start_time = None
        self.monster = None

        self._create_horde()

        # Make the Play button.
        self.play_button = Button(self, "Play")

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()

            if self.stats.game_active: 
                self.soldier.update()
                self._update_bullets()
                self._update_zombies() 
                if self.machinegun != None:
                    self._update_machinegun()
                if self.weapon_start_time != None:
                    self._update_bonus()
                if self.monster != None:
                    self._update_monster()

            self._update_screen()

    def _check_events(self):
        """Respond to keypresses and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            # Reset the game settings.
            self.settings.initialize_dynamic_settings()

            # Reset the game statistics.
            self.stats.reset_stats()
            self.stats.game_active = True
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_soldiers()

            # Get rid of any remaining zombies and bullets.
            self.zombies.empty()
            self.bullets.empty()
            
            # Create a new horde and center the soldier.
            self._create_horde()
            self.soldier.center_soldier()

            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_DOWN:
            self.soldier.moving_down = True
        elif event.key == pygame.K_UP:
            self.soldier.moving_up = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_DOWN:
            self.soldier.moving_down = False
        elif event.key == pygame.K_UP:
            self.soldier.moving_up = False

    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.right >= self.screen.get_rect().width:
                 self.bullets.remove(bullet)

        self._check_bullet_zombie_collisions()
        if self.monster != None:
            self._check_bullet_monster_collisions()

    def _check_bullet_zombie_collisions(self):
        """Respond to bullet-zombie collisions."""
        # Remove any bullets and zombies that have collided.
        collisions = pygame.sprite.groupcollide(
                self.bullets, self.zombies, True, True)

        if collisions:
            for zombies in collisions.values():
                self.stats.score += self.settings.zombie_points * len(zombies)
            self.sb.prep_score()
            self.sb.check_high_score()

        if not self.zombies:
            # Destroy existing bullets and create new horde.
            self.bullets.empty()
            self._create_horde()
            self.settings.increase_speed()

            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()

    def _check_bullet_machinegun_collisions(self):
        """Respond to machinegun-bullet collisions.""" 
        # Check bullet-machinegun collisions
        if pygame.sprite.spritecollideany(self.machinegun, self.bullets):
            self.machinegun = None 
            self.weapon_start_time = pygame.time.get_ticks()
            self.settings.bullets_allowed = 15
            self.settings.bullet_color = (255, 0, 0)
            self.settings.bullet_width = 25

    def _check_bullet_monster_collisions(self):
        """Respond to monster-bullet collisions."""
        # Check bullet-machinegun collisions
        colliding_bullet = pygame.sprite.spritecollideany(self.monster, self.bullets)
        self.bullets.remove(colliding_bullet)
        if colliding_bullet:
            self.monster.hitpoints -= 1
            if self.monster.hitpoints < 1:
                self.monster = None
                self.stats.score += self.settings.monster_points

    def _update_zombies(self):
        """
        Check if the horde is at an edge,
          then update the positions of all zombies in the horde.
        """
        self._check_horde_edges()
        self.zombies.update()

        # Look for zombie-soldier collisions.
        if pygame.sprite.spritecollideany(self.soldier, self.zombies):
            self._soldier_hit()

        # Look for zombies hitting the left side of the screen.
        self._check_zombies_left()

    def _check_zombies_left(self):
        """Check if any zombies or monsters have reached the left side of the screen.""" 
        screen_rect = self.screen.get_rect()
        for zombie in self.zombies.sprites():
            if zombie.rect.left <= screen_rect.left:
                # Treat this the same as if the soldier got hit.
                self._soldier_hit()
                break
        if self.monster != None:
            if self.monster.rect.left <= screen_rect.left:
                self._soldier_hit()

    def _update_machinegun(self):
        """Check machinegun timer and collisions with bullet"""
        if self.machinegun.check_timer() >= self.settings.weapon_appear_time:
            self.machinegun = None
        else:
            self._check_bullet_machinegun_collisions()

    def _update_bonus(self):
        """Check bonus timer in case it should end"""
        if pygame.time.get_ticks() - self.weapon_start_time >= self.settings.weapon_bonus_time:
            self.weapon_start_time = None
            self.settings.bullets_allowed = self.settings.default_bullets_allowed
            self.settings.bullet_color = self.settings.default_bullets_color
            self.settings.bullet_width = self.settings.default_bullets_width
        
    def _soldier_hit(self):
        """Respond to the soldier being hit by an zombie."""
        if self.stats.soldiers_left > 0:
            # Decrement soldiers_left, and update scoreboard.
            self.stats.soldiers_left -= 1
            self.sb.prep_soldiers()
            
            # Get rid of any remaining zombies,bonus, monster and bullets.
            self.zombies.empty()
            self.bullets.empty()
            self.monster = None
            self.machinegun = None
            
            # Create a new horde and center the soldier.
            self._create_horde()
            self.soldier.center_soldier()
            
            # Pause.
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)   

    def _create_horde(self):
        """Create the horde of zombies."""
        # Create an zombie and find the number of zombies in a row.
        # Spacing between each zombie is equal to one zombie width.
        zombie = Zombie(self)
        zombie_width, zombie_height = zombie.rect.size
        available_space_y = self.settings.screen_height - (2 * zombie_height)
        number_zombies_y = available_space_y // (2 * zombie_height)
        
        # Determine the number of rows of zombie s that fit on the screen.
        soldier_width = self.soldier.rect.width
        available_space_x = (self.settings.screen_width -
                                (5 * zombie_width) - soldier_width)
        number_columns = available_space_x // (2 * zombie_width)
        
        # Create the full horde of zombies.
        for row_number in range(number_columns):
            for zombie_number in range(number_zombies_y):
                self._create_zombie(zombie_number, row_number)

    def _create_zombie(self, zombie_number, column_number):
        """Create an zombie and place it in the column."""
        zombie = Zombie(self)
        zombie_width, zombie_height = zombie.rect.size
        zombie.y = zombie_height + 2 * zombie_height * zombie_number
        zombie.rect.y = zombie.y
        zombie.rect.x = zombie.rect.width*5 + 2 * zombie.rect.width * column_number
        self.zombies.add(zombie)

    def _check_horde_edges(self):
        """Respond appropriately if any zombies have reached an edge.""" 
        for zombie in self.zombies.sprites():
            if zombie.check_edges():
                self._change_horde_direction()
                self._create_machinegun()
                self._create_monster()
                break
    
    def _check_monster_edges(self):
        """Respond appropriately the monster has reached an edge."""
        if self.monster!=None and self.monster.check_edges():
            self._change_monster_direction()
            
    def _change_horde_direction(self):
        """Drop the entire horde and change the horde's direction. Also use this moment to creat machinegun"""
        for zombie in self.zombies.sprites():
            zombie.rect.x -= self.settings.horde_advance_speed
        self.settings.horde_direction *= -1

    def _change_monster_direction(self):
        """Change Monster direction"""
        self.settings.monster_direction *= -1

    def _create_machinegun(self):
        # Create machinegun with 5% probability
        if(random.random() < self.settings.weapon_frequency and self.machinegun == None):
            self.machinegun = Machinegun(self, pygame.time.get_ticks())

    def _create_monster(self):
        # Create monster with 5% probability
        if(random.random() < self.settings.monster_frequency and self.monster == None):
            self.monster = Monster(self)

    def _update_monster(self):
        """
        Check if the monster is at an edge,
          then update the position.
        """  
        self._check_monster_edges()  
        self.monster.update()

        # Look for monster-soldier collisions.
        if self.monster != None and self.soldier != None: 
            if self.monster.rect.colliderect(self.soldier.rect):
                self._soldier_hit()

        # Look for monster hitting the left side of the screen.
        self._check_zombies_left()

    def _update_screen(self):
        """Update images on the screen, and flip to the new screen."""
        self.screen.fill(self.settings.bg_color)
        self.soldier.blitme()
        if (self.machinegun != None):
            self.machinegun.blitme()
        if (self.monster != None):
            self.monster.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.zombies.draw(self.screen)

        # Draw the score information.
        self.sb.show_score()

        # Draw the play button if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()

        pygame.display.flip()


if __name__ == '__main__':  
    # Make a game instance, and run the game.
    ai = ZombieInvasion()
    ai.run_game()
