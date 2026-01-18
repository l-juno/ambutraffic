import pygame

class Vehicle:
  def __init__(self, x: int, y: int, type: str, speed=0.0, angle=90):
    self.position = pygame.Vector2(x, y)
    self.speed = speed
    self.angle = angle
    self.original_image = pygame.image.load(f"assets/{type}.png").convert_alpha()
    self.image = pygame.transform.rotate(self.original_image, -self.angle)
  
    self.rect = self.image.get_rect()
    self.rect.center = (self.position.x, self.position.y)