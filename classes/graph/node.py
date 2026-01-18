import pygame

class Node:
    def __init__(self, node_id, x, y):
        self.id = node_id
        self.position = pygame.Vector2(x, y)

    def get_x(self):
        return self.position.x

    def get_y(self):
        return self.position.y

    def get_pos(self):
        return self.position


    