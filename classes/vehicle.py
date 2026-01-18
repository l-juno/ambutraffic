import math
import pygame
from classes.traffic_light.light_state import LightState
# for zone
SCREEN_WIDTH = 1000 
SCREEN_HEIGHT = 800
AMBULANCE_ZONE_RADIUS = 300
TRAFFIC_ZONE_RADIUS = 200
ZONE_CENTER_X = SCREEN_WIDTH // 2
ZONE_CENTER_Y = SCREEN_HEIGHT // 2

LEFT_TURN_OPPOSING = {
    "N_left": ["S_straight", "S_right"],  # North left yields to South straight/right
    "S_left": ["N_straight", "N_right"],  # South left yields to North straight/right
    "E_left": ["W_straight", "W_right"],  # East left yields to West straight/right
    "W_left": ["E_straight", "E_right"],  # West left yields to East straight/right
}

LEFT_TURN_WAIT_NODE_INDEX = 2  # nodes[2] is the left-turn lane node (24, 25, 26, 27)

class Vehicle:
    def __init__(self, route, speed, type: str, traffic_light):
        self.route = route
        self.current_index = 0
        self.type = type
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

        # Left turn yielding
        self.LEFT_TURN_YIELD_DISTANCE = 180  # Distance to check for opposing vehicles
        self.is_left_turn = route.id in LEFT_TURN_OPPOSING
        self.opposing_routes = LEFT_TURN_OPPOSING.get(route.id, [])
        
        # Store the wait node position (nodes 24, 25, 26, 27) for left turns
        self.left_turn_wait_position = None
        if self.is_left_turn and len(route.nodes) > LEFT_TURN_WAIT_NODE_INDEX:
            self.left_turn_wait_position = route.nodes[LEFT_TURN_WAIT_NODE_INDEX].position.copy()
        
        # Calculate the path index where the left turn wait point is
        # This is around where nodes[2] is in the path (after the approach edges)
        self.left_turn_wait_path_index = self._find_left_turn_wait_index()
        
        # Track if we're waiting at the left turn point
        self.waiting_at_left_turn = False

        # zone
        self.isInAmbulanceZone = False
        self.isInTrafficZone = False

        self.original_image = pygame.image.load(
            f"assets/{type}.png"
        ).convert_alpha()
        self.image = self.original_image
        self.rect = self.image.get_rect(center=self.position)
    
    def _find_left_turn_wait_index(self):
        """Find the path index closest to the left-turn lane node (nodes[2])"""
        if not self.is_left_turn or len(self.route.nodes) < 3:
            return -1
        
        wait_node_pos = self.route.nodes[LEFT_TURN_WAIT_NODE_INDEX].position
        min_dist = float("inf")
        closest_index = -1
        
        for i, pos in enumerate(self.route.path):
            dist = (pos - wait_node_pos).length()
            if dist < min_dist:
                min_dist = dist
                closest_index = i
        
        return closest_index
    
    def _get_node_path_index(self, node_index):
        """Find the path index closest to the given route node index."""
        if node_index >= len(self.route.nodes):
            return len(self.route.path) - 1
        
        node_pos = self.route.nodes[node_index].position
        min_dist = float("inf")
        closest_index = -1
        
        for i, pos in enumerate(self.route.path):
            dist = (pos - node_pos).length()
            if dist < min_dist:
                min_dist = dist
                closest_index = i
        
        return closest_index


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

    def has_opposing_traffic(self, vehicles):
        if not self.is_left_turn:
            return False
      
        intersection_center = pygame.Vector2(ZONE_CENTER_X, ZONE_CENTER_Y)
        
        for other in vehicles:
            if other is self or other.finished:
                continue
            
            # check if the other vehicle is on an opposing route
            if other.route.id not in self.opposing_routes:
                continue
            other_dist_to_center = (other.position - intersection_center).length()
            
            # If the opposing vehicle is within the yield distance and still has path ahead
            if other_dist_to_center < self.LEFT_TURN_YIELD_DISTANCE:
                remaining_path = len(other.route.path) - other.current_index
                total_path = len(other.route.path)
                
                # If they're in the first 70% of their route, they're still a threat
                if remaining_path > total_path * 0.3:
                    return True
        
        return False
    
    def is_approaching_left_turn_wait(self):
        if not self.is_left_turn or self.left_turn_wait_position is None:
            return False
        dist_to_wait = (self.position - self.left_turn_wait_position).length()
        return (self.current_index < self.left_turn_wait_path_index and dist_to_wait < 100)
    
    def is_at_left_turn_wait(self):
        if not self.is_left_turn or self.left_turn_wait_position is None:
            return False
        
        dist_to_wait = (self.position - self.left_turn_wait_position).length()
        return dist_to_wait < 5  # Within 5 pixels of the wait position

    def get_nearest_vehicle_ahead(self, vehicles, forward):
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
        
        return nearest_dist

    def update(self, vehicles):
        if self.finished:
            return

        if self.current_index >= len(self.route.path) - 1:
            self.finished = True
            return
        

        
        # Red light check - stop at nodes[2] (entry point to intersection)
        if self.get_traffic_light_state() in (LightState.NS_RED, LightState.EW_RED):
            if self.is_facing_target(self.position, self.angle, self.traffic_light.pos):
                stop_position = self.route.nodes[2].position
                dist_to_stop = (self.position - stop_position).length()
                
                # If at stop position, stay stopped
                if dist_to_stop < 10:
                    return
                
                # If approaching the stop position, move toward it and stop there
                if dist_to_stop < 80 and self.current_index <= self._get_node_path_index(2):
                    move_vec = stop_position - self.position
                    if move_vec.length() > 0:
                        forward = move_vec.normalize()
                        
                        # Check for vehicles ahead - don't overlap!
                        nearest_dist = self.get_nearest_vehicle_ahead(vehicles, forward)
                        buffer = 5
                        stop_gap = self.STOP_GAP + buffer
                        
                        # Calculate how far we can move
                        move_dist = min(self.max_speed, dist_to_stop - 5)
                        
                        # Stop if there's a vehicle too close ahead
                        if nearest_dist < stop_gap:
                            move_dist = 0
                        elif nearest_dist < self.SAFE_GAP + buffer:
                            # Slow down when approaching another vehicle
                            t = (nearest_dist - stop_gap) / (self.SAFE_GAP - self.STOP_GAP)
                            move_dist = min(move_dist, max(self.MIN_SPEED, self.max_speed * t))
                        
                        if move_dist > 0:
                            self.position += forward * move_dist
                            self.rect.center = self.position
                            # Update angle
                            target_angle = math.degrees(math.atan2(-forward.y, forward.x)) - 90
                            diff = (target_angle - self.angle + 180) % 360 - 180
                            self.angle += diff * 0.2
                            self.image = pygame.transform.rotate(self.original_image, self.angle)
                            self.rect = self.image.get_rect(center=self.rect.center)
                    self.point_in_ambulance_zone(self.position.x, self.position.y)
                    self.point_in_traffic_zone(self.position.x, self.position.y)
                    return

        # Left turn yielding logic - wait at the designated wait node (24, 25, 26, 27)
        if self.is_left_turn and self.left_turn_wait_position is not None:
            # If we're already at the wait position, check if we can proceed
            if self.is_at_left_turn_wait():
                if self.has_opposing_traffic(vehicles):
                    # Stay at the wait position
                    self.waiting_at_left_turn = True
                    self.point_in_ambulance_zone(self.position.x, self.position.y)
                    self.point_in_traffic_zone(self.position.x, self.position.y)
                    return
                else:
                    # Clear to proceed
                    self.waiting_at_left_turn = False
            
            # If approaching the wait point and there's opposing traffic,
            # move to the wait position and stop there
            elif self.is_approaching_left_turn_wait() and self.has_opposing_traffic(vehicles):
                # Move toward the wait position instead of the normal target
                move_vec = self.left_turn_wait_position - self.position
                distance = move_vec.length()
                
                if distance > 0:
                    forward = move_vec.normalize()
                    
                    # Check for vehicles ahead - don't overlap!
                    nearest_dist = self.get_nearest_vehicle_ahead(vehicles, forward)
                    buffer = 5
                    stop_gap = self.STOP_GAP + buffer
                    
                    # Calculate how far we can move
                    move_dist = self.max_speed
                    
                    # Stop if there's a vehicle too close ahead
                    if nearest_dist < stop_gap:
                        move_dist = 0
                    elif nearest_dist < self.SAFE_GAP + buffer:
                        # Slow down when approaching another vehicle
                        t = (nearest_dist - stop_gap) / (self.SAFE_GAP - self.STOP_GAP)
                        move_dist = max(self.MIN_SPEED, self.max_speed * t)
                    
                    if distance <= move_dist and move_dist > 0:
                        # Snap to the wait position
                        self.position = self.left_turn_wait_position.copy()
                        self.current_index = self.left_turn_wait_path_index
                        self.waiting_at_left_turn = True
                    elif move_dist > 0:
                        self.position += forward * move_dist
                    
                    self.rect.center = self.position
                    self.point_in_ambulance_zone(self.position.x, self.position.y)
                    self.point_in_traffic_zone(self.position.x, self.position.y)
                    
                    # Update angle
                    target_angle = math.degrees(math.atan2(-forward.y, forward.x)) - 90
                    diff = (target_angle - self.angle + 180) % 360 - 180
                    self.angle += diff * 0.2
                    self.image = pygame.transform.rotate(self.original_image, self.angle)
                    self.rect = self.image.get_rect(center=self.rect.center)
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
