import random
import pygame
from pygame.sprite import Sprite

class Machinegun(Sprite):
    """A class to represent a machinegun bonus."""

    def __init__(self, ai_game, start_time):
        """Initialize the machinegun and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.start_time = start_time

        # Load the machinegun image and set its rect attribute.
        self.image = pygame.image.load('images/machinegun.png')
        self.rect = self.image.get_rect()

        # Start each new zombie near the top right of the screen.
        self.rect.x = random.randint(2*self.rect.width, self.screen.get_rect().width - self.rect.width)
        self.rect.y = random.randint(0, self.screen.get_rect().height)

    def check_timer(self):
        if self.start_time is not None:  # If the timer has been started...
            return pygame.time.get_ticks() - self.start_time

    def blitme(self):
        """Draw the machinegun at its location."""
        self.screen.blit(self.image, self.rect)