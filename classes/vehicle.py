import math
import pygame

class Vehicle:
  def __init__(self, route, speed, type: str):
    self.route = route
    self.current_index = 0
    self.finished = False
    start_node = route.nodes[0]
    self.position = start_node.position.copy()
    
    self.speed = speed
    self.original_image = pygame.image.load(f"assets/{type}.png").convert_alpha()
    self.image = self.original_image

    self.rect = self.image.get_rect(center=self.position)
    
    
  def update(self):
    if self.finished:
        return
  
    if self.current_index >= len(self.route.nodes) - 1:
        self.finished = True
        return

    current_node = self.route.nodes[self.current_index]
    next_node = self.route.nodes[self.current_index + 1]

    target = next_node.position
    direction = target - self.position
    distance = direction.length()

    if distance < self.speed:
            self.position = target.copy()
            self.current_index += 1
            self.rect.center = self.position
            return

    direction = direction.normalize()
    self.position += direction * self.speed
    self.rect.center = self.position
    
    self.angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90
    self.image = pygame.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect(center=self.rect.center)


    