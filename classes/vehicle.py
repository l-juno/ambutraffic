import math
import pygame
# for zone
SCREEN_WIDTH = 1000 
SCREEN_HEIGHT = 800
AMBULANCE_ZONE_RADIUS = 300
TRAFFIC_ZONE_RADIUS = 200
ZONE_CENTER_X = SCREEN_WIDTH // 2
ZONE_CENTER_Y = SCREEN_HEIGHT // 2
from classes.traffic_light.light_state import LightState
class Vehicle:
    def __init__(self, route, speed, type: str, traffic_light):
        self.route = route
        self.current_index = 0
        self.finished = False
        self.traffic_light = traffic_light

        self.position = route.nodes[0].position.copy()
        self.max_speed = speed
        self.speed = speed

        self.angle = 0

        # spacing / safety
        self.LANE_WIDTH = 7
        self.STOP_GAP = 25
        self.SAFE_GAP = 50
        self.MIN_SPEED = 0.15

        # zone
        self.isInAmbulanceZone = False
        self.isInTrafficZone = False

        

        self.original_image = pygame.image.load(
            f"assets/{type}.png"
        ).convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=self.position)


    def point_in_ambulance_zone(self, x, y):
      self.isInAmbulanceZone = False
      distance = math.hypot(x - ZONE_CENTER_X, y - ZONE_CENTER_Y)
      if distance < AMBULANCE_ZONE_RADIUS:
          self.isInAmbulanceZone = True

    def point_in_traffic_zone(self, x, y):
      self.isInTrafficZone = False
      distance = math.hypot(x - ZONE_CENTER_X, y - ZONE_CENTER_Y)
      if distance < TRAFFIC_ZONE_RADIUS:
          self.isInTrafficZone = True

    def update(self, vehicles):
        if self.finished:
            return

        if self.current_index >= len(self.route.path) - 1:
            self.finished = True
            return
        
        if self.get_traffic_light_state() in (LightState.NS_RED, LightState.EW_RED):
            if self.is_facing_target(self.position, self.angle, self.traffic_light.pos):
                if self.position == self.route.nodes[2].position:
                    return


        target = self.route.path[self.current_index + 1]

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

            # if other.route.id != self.route.id:
            #     continue

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

        # if self.isInTrafficZone:
        #     if self.get_traffic_light_state() in (LightState.NS_RED, LightState.EW_RED):
        #         if self.is_facing_target(self.position, self.angle, self.traffic_light.pos):
        #                 speed_now = self.max_speed * 0.5

        if self.get_traffic_light_state() in (LightState.NS_RED, LightState.EW_RED):
                if self.is_facing_target(self.position, self.angle, self.traffic_light.pos):
                    if self.current_index < 2 and self.isInTrafficZone:
                        speed_now = self.max_speed * 0.5

        buffer = 5
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

        self.point_in_ambulance_zone(self.position.x, self.position.y)
        self.point_in_traffic_zone(self.position.x, self.position.y)

        target_angle = math.degrees(math.atan2(-forward.y, forward.x)) - 90

        diff = (target_angle - self.angle + 180) % 360 - 180
        self.angle += diff * 0.2

        self.image = pygame.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def get_traffic_light_state(self):
        return self.traffic_light.state
    
    
    def angle_to_target(self, from_pos, to_pos):
        dx = to_pos.x - from_pos.x
        dy = to_pos.y - from_pos.y
        return math.degrees(math.atan2(-dy, dx))


    def normalize_angle(self, angle):
        """
        Normalize angle to range [-180, 180)
        """
        return (angle + 180) % 360 - 180


    def is_facing_target(
        self,
        vehicle_pos,
        vehicle_angle,   # sprite angle
        target_pos,
        tolerance_deg=20
    ):
        target_angle = self.angle_to_target(vehicle_pos, target_pos)

        # Convert sprite rotation → true heading
        heading = vehicle_angle + 90

        diff = self.normalize_angle(target_angle - heading)

        return abs(diff) <= tolerance_deg
