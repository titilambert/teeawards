from libs.lib import tee_db
from datetime import datetime, timedelta

class Achievement():
    def __init__(self, name, image, description, condition):
        self.name = name
        self.image = image
        self.description = description
        self.condition = condition

    def has_achievements(self, player):
        return self.condition(self, player)
