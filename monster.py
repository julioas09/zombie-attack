import pygame
import random
from pygame.sprite import Sprite
 
class Monster(Sprite):
    """A class to represent a monster."""

    def __init__(self, ai_game):
        """Initialize the monster and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        self.hitpoints = 3

        # Load the zombie image and set its rect attribute.
        self.image = pygame.image.load('images/monster.png')
        self.rect = self.image.get_rect()

        # Start monster near the top right of the screen.
        self.rect.x = self.screen.get_rect().width - self.rect.width
        self.rect.y = random.randint(0, self.screen.get_rect().height - self.rect.height)

        # Store the monster's exact position.
        self.y = float(self.rect.y)
        self.x = float(self.rect.x)

    def check_edges(self):
        """Return True if monster is at edge of screen."""
        screen_rect = self.screen.get_rect()
        if self.rect.bottom >= screen_rect.bottom or self.rect.bottom <= self.rect.height:
            return True

    def update(self):
        """Move the monster in diagonal, slowed than zombies."""
        self.y += (self.settings.zombie_speed/2 *
                        self.settings.monster_direction)
        self.rect.y = self.y

        self.x -= self.settings.zombie_speed/2
        self.rect.x = self.x
    
    def blitme(self):
        """Draw the monster at its location."""
        self.screen.blit(self.image, self.rect)
