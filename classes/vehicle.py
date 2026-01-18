import math
import pygame

class Vehicle:
    def __init__(self, route, speed, type: str):
        self.route = route
        self.current_index = 0
        self.finished = False

        self.position = route.nodes[0].position.copy()
        self.max_speed = speed
        self.speed = speed

        self.angle = 0

        # spacing / safety
        self.LANE_WIDTH = 18
        self.STOP_GAP = 25
        self.SAFE_GAP = 50
        self.MIN_SPEED = 0.15

        self.original_image = pygame.image.load(
            f"assets/{type}.png"
        ).convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=self.position)

    def update(self, vehicles):
        if self.finished:
            return

        if self.current_index >= len(self.route.nodes) - 1:
            self.finished = True
            return

        next_node = self.route.nodes[self.current_index + 1]
        target = next_node.position

        move_vec = target - self.position
        distance = move_vec.length()

        if distance == 0:
            return

        forward = move_vec.normalize()
        left = pygame.Vector2(-forward.y, forward.x)

        nearest_dist = float("inf")
        for other in vehicles:
            if other is self or other.finished:
                continue

            to_other = other.position - self.position
            d = to_other.length()

            if d == 0:
                continue

            if forward.dot(to_other) <= 0:
                continue

            side_dist = abs(to_other.dot(left))
            if side_dist > self.LANE_WIDTH:
                continue

            if d < nearest_dist:
                nearest_dist = d

        speed_now = self.max_speed

        buffer = 20
        stop_dist = self.STOP_GAP + buffer
        safe_dist = self.SAFE_GAP + buffer

        if nearest_dist < stop_dist:
            speed_now = 0.0
        elif nearest_dist < safe_dist:
            t = (nearest_dist - stop_dist) / (safe_dist - stop_dist)
            speed_now = max(self.MIN_SPEED, self.max_speed * t)

        if distance <= speed_now:
            self.position = target.copy()
            self.current_index += 1
        else:
            self.position += forward * speed_now

        self.rect.center = self.position


        target_angle = math.degrees(math.atan2(-forward.y, forward.x)) - 90

        diff = (target_angle - self.angle + 180) % 360 - 180
        self.angle += diff * 0.2

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)



    