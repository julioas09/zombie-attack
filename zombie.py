import pygame
from pygame.sprite import Sprite
 
class Zombie(Sprite):
    """A class to represent a single zombie in the horde."""

    def __init__(self, ai_game):
        """Initialize the zombie and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Load the zombie image and set its rect attribute.
        self.image = pygame.image.load('images/zombie.png')
        self.rect = self.image.get_rect()

        # Start each new zombie near the top right of the screen.
        self.rect.x = self.screen.get_rect().width - self.rect.width
        self.rect.y = self.rect.height

        # Store the zombie's exact vertical position.
        self.y = float(self.rect.y)

    def check_edges(self):
        """Return True if zombie is at edge of screen."""
        screen_rect = self.screen.get_rect()
        if self.rect.bottom >= screen_rect.bottom or self.rect.bottom <= self.rect.height:
            return True

    def update(self):
        """Move the zombie up of down."""
        self.y += (self.settings.zombie_speed *
                        self.settings.horde_direction)
        self.rect.y = self.y
