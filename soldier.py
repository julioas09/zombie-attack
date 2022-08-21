import pygame
 
from pygame.sprite import Sprite
 
class Soldier(Sprite):
    """A class to manage the soldier."""
 
    def __init__(self, ai_game):
        """Initialize the soldier and set its starting position."""
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.screen_rect = ai_game.screen.get_rect()

        # Load the soldier image and get its rect.
        self.image = pygame.image.load('images/soldier64.png')
        self.rect = self.image.get_rect()

        # Start each new soldier at the bottom center of the screen.
        self.rect.midleft = self.screen_rect.midleft

        # Store a decimal value for the soldier's horizontal position.
        self.y = float(self.rect.y)

        # Movement flags
        self.moving_down = False
        self.moving_up = False

    def update(self):
        """Update the soldier's position based on movement flags."""
        # Update the soldier's y value, not the rect.
        if self.moving_down and self.rect.bottom < self.screen_rect.bottom:
            self.y += self.settings.soldier_speed
        if self.moving_up and self.rect.top > 0:
            self.y -= self.settings.soldier_speed

        # Update rect object from self.y.
        self.rect.y = self.y

    def blitme(self):
        """Draw the soldier at its current location."""
        self.screen.blit(self.image, self.rect)

    def center_soldier(self):
        """Center the soldier on the screen."""
        self.rect.midleft = self.screen_rect.midleft
        self.y = float(self.rect.y)
