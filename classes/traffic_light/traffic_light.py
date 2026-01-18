import pygame
from classes.traffic_light.light_state import LightState

class TrafficLight:
    def __init__(self, pos, initial_state):
        self.pos = pos
        self.state = initial_state
        self.timer = 0.0

        self.green_time = 180.0
        self.yellow_time = 120.0
        self.red_time = 300.0

    def update(self):
        self.timer += 1

        if self.state in (LightState.NS_GREEN, LightState.EW_GREEN):
            if self.timer >= self.green_time:
                self._advance()

        elif self.state in (LightState.NS_YELLOW, LightState.EW_YELLOW):
            if self.timer >= self.yellow_time:
                self._advance()

        elif self.state in (LightState.NS_RED, LightState.EW_RED):
            if self.timer >= self.red_time:
                self._advance()

    def _advance(self):
        self.timer = 0.0

        if self.state == LightState.NS_GREEN:
            self.state = LightState.NS_YELLOW

        elif self.state == LightState.NS_YELLOW:
            self.state = LightState.NS_RED

        elif self.state == LightState.NS_RED:
            self.state = LightState.EW_GREEN

        elif self.state == LightState.EW_GREEN:
            self.state = LightState.EW_YELLOW

        elif self.state == LightState.EW_YELLOW:
            self.state = LightState.EW_RED

        elif self.state == LightState.EW_RED:
            self.state = LightState.NS_GREEN

    def draw(self, screen):
        if self.state in (LightState.NS_GREEN, LightState.EW_GREEN):
            color = (0, 255, 0)
        elif self.state in (LightState.NS_YELLOW, LightState.EW_YELLOW):
            color = (255, 255, 0)
        else:
            color = (255, 0, 0)

        pygame.draw.circle(screen, color, self.pos, 6)
