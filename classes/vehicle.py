import math
import pygame

class Vehicle:
  def __init__(self, route, speed, type: str, angle, NODE_POS):
    self.route = route
    self.NODE_POS = NODE_POS
    node_initial_id = route.pop(0)
    x_initial = NODE_POS[node_initial_id][0]
    y_initial = NODE_POS[node_initial_id][1]
    
    self.position = pygame.Vector2(x_initial, y_initial)
    
    self.speed = speed
    self.angle = angle
    self.original_image = pygame.image.load(f"assets/{type}.png").convert_alpha()
    self.image = pygame.transform.rotate(self.original_image, -self.angle)

    self.rect = self.image.get_rect()
    self.rect.center = (x_initial, y_initial)
    
    
  def update(self):
    if not self.route:
        return

    destination_node = self.NODE_POS[self.route[0]]
    destination_position = pygame.Vector2(destination_node.x, destination_node.y)

    direction = destination_position - self.position
    distance = direction.length()

    if distance < 5:
        self.position = destination_position  
        self.route.pop(0)
        self.rect.center = self.position
        return

    direction = direction.normalize()
    self.position += direction * self.speed
    self.rect.center = self.position
    
    self.angle = math.degrees(math.atan2(-direction.y, direction.x)) - 90
    self.image = pygame.transform.rotate(self.original_image, self.angle)
    self.rect = self.image.get_rect(center=self.rect.center)

    