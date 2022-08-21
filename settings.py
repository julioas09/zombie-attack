class Settings:
    """A class to store all settings for Zombie Attack."""

    def __init__(self):
        """Initialize the game's static settings."""
        # Screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230, 230, 230)

        # Soldier settings
        self.soldier_limit = 3

        # Bullet settings
        self.bullet_width = 15
        self.bullet_height = 3
        self.bullet_color = (60, 60, 60)
        self.bullets_allowed = 3

        # Zombie settings
        self.fleet_advance_speed = 30

        # How quickly the game speeds up
        self.speedup_scale = 1.1
        # How quickly the zombie point values increase
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Initialize settings that change throughout the game."""
        self.soldier_speed = 1.5
        self.bullet_speed = 3.0
        self.zombie_speed = 1.0

        # fleet_direction of 1 represents down; -1 represents up.
        self.fleet_direction = -1

        # Scoring
        self.zombie_points = 50

    def increase_speed(self):
        """Increase speed settings and zombie point values."""
        self.soldier_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.zombie_speed *= self.speedup_scale

        self.zombie_points = int(self.zombie_points * self.score_scale)
