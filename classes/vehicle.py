# import math
# import pygame

# class Vehicle:
#   def __init__(self, route, speed, type: str, angle, NODE_POS):
#     self.safe_dist = 45
#     self.stop_dist = 25
#     self.max_speed = speed

#     self.route = list(route)
#     self.NODE_POS = NODE_POS

#     node_initial_id = self.route.pop(0)

#     start = self.NODE_POS[node_initial_id]
#     x_initial = start.x
#     y_initial = start.y

#     self.position = pygame.Vector2(x_initial, y_initial)
#     self.speed = speed
#     self.angle = angle
#     self.original_image = pygame.image.load(f"assets/{type}.png").convert_alpha()
#     self.image = pygame.transform.rotate(self.original_image, -self.angle)

#     self.rect = self.image.get_rect(center=(x_initial, y_initial))



#   def update(self, vehicles):
#       if not self.route:
#           return

#       destination_node = self.NODE_POS[self.route[0]]
#       destination_position = pygame.Vector2(destination_node.x, destination_node.y)

#       move_vec = destination_position - self.position
#       dist_to_dest = move_vec.length()

#       if dist_to_dest < 5:
#           self.position = destination_position
#           self.route.pop(0)
#           self.rect.center = self.position
#           return

#       forward = move_vec.normalize()

#       left = pygame.Vector2(-forward.y, forward.x)

#       nearest_ahead = None
#       nearest_ahead_dist = float("inf")

#       # is it in my lane
#       LANE_WIDTH = 18
#       # distance before stop
#       STOP_GAP = 25 
#       # distance before slowing
#       SAFE_GAP = 50
#       MIN_SPEED = 0.15

#       for other in vehicles:
#           if other is self:
#               continue

#           to_other = other.position - self.position
#           d = to_other.length()
#           if d == 0:
#               continue

#           if forward.dot(to_other) <= 0:
#               continue

#           side_dist = abs(to_other.dot(left))
#           if side_dist > LANE_WIDTH:
#               continue

#           if d < nearest_ahead_dist:
#               nearest_ahead_dist = d
#               nearest_ahead = other


#       speed_now = self.max_speed

#       if nearest_ahead is not None:
#           MY_R = 10
#           OTHER_R = 10
#           buffer = MY_R + OTHER_R

#           stop_dist = STOP_GAP + buffer
#           safe_dist = SAFE_GAP + buffer

#           if nearest_ahead_dist <= stop_dist:
#               speed_now = 0.0
#           elif nearest_ahead_dist < safe_dist:
#               t = (nearest_ahead_dist - stop_dist) / (safe_dist - stop_dist)
#               t = max(0.0, min(1.0, t))
#               speed_now = self.max_speed * t
#               if 0.0 < speed_now < MIN_SPEED:
#                   speed_now = MIN_SPEED


#       # moving the vehicle
#       self.position += forward * speed_now
#       self.rect.center = self.position

#       # rotating the vehicle
#       self.angle = math.degrees(math.atan2(-forward.y, forward.x)) - 90
#       self.image = pygame.transform.rotate(self.original_image, self.angle)
#       self.rect = self.image.get_rect(center=self.rect.center)

import math
import pygame

class Vehicle:
  def __init__(self, route_node_ids, speed, type: str, angle, NODE_POS):
      # --- driving params ---
      self.max_speed = float(speed)
      self.safe_gap = 50      # start slowing when closer than this
      self.stop_gap = 25      # hard stop when closer than this
      self.lane_tol = 18      # sideways tolerance for "same lane"
      self.min_speed = 0.15   # optional: prevents tiny speeds from looking stuck

      # --- route state ---
      self.route = list(route_node_ids)
      self.current_index = 0
      self.finished = False
      self.NODE_POS = NODE_POS

      # start position at first node
      start = self.NODE_POS[self.route[0]]
      self.position = pygame.Vector2(start.x, start.y)

      # sprite
      self.angle = angle
      self.original_image = pygame.image.load(f"assets/{type}.png").convert_alpha()
      self.image = pygame.transform.rotate(self.original_image, -self.angle)
      self.rect = self.image.get_rect(center=self.position)

  def update(self, vehicles):
      if self.finished:
          return

      # If we're at the last node, we're done
      if self.current_index >= len(self.route) - 1:
          self.finished = True
          return

      # --- PATH FOLLOWING: compute target + forward direction ---
      next_id = self.route[self.current_index + 1]
      target_node = self.NODE_POS[next_id]
      target = pygame.Vector2(target_node.x, target_node.y)

      move_vec = target - self.position
      dist_to_target = move_vec.length()

      # Snap to the node if we're close
      SNAP_DIST = 5
      if dist_to_target < speed_now:
          self.position = target
          self.current_index += 1
          self.rect.center = self.position
          return

      forward = move_vec.normalize()
      left = pygame.Vector2(-forward.y, forward.x)

      # --- MOTION CONTROL: find nearest vehicle ahead in same lane ---
      nearest_ahead_dist = float("inf")
      nearest_ahead = None

      for other in vehicles:
          if other is self or other.finished:
              continue

          to_other = other.position - self.position
          d = to_other.length()
          if d <= 0:
              continue

          # Must be in front
          if forward.dot(to_other) <= 0:
              continue

          # Must be roughly in same lane (small sideways offset)
          side_dist = abs(to_other.dot(left))
          if side_dist > self.lane_tol:
              continue

          if d < nearest_ahead_dist:
              nearest_ahead_dist = d
              nearest_ahead = other

      # --- choose speed ---
      speed_now = self.max_speed

      if nearest_ahead is not None:
          # Use small "physics radii" instead of sprite size
          buffer = 20  # roughly car length/2 + car length/2; tweak

          stop_dist = self.stop_gap + buffer
          safe_dist = self.safe_gap + buffer

          if nearest_ahead_dist <= stop_dist:
              speed_now = 0.0
          elif nearest_ahead_dist < safe_dist:
              # slow down smoothly between safe_dist and stop_dist
              t = (nearest_ahead_dist - stop_dist) / (safe_dist - stop_dist)
              t = max(0.0, min(1.0, t))
              speed_now = self.max_speed * t
              if 0.0 < speed_now < self.min_speed:
                  speed_now = self.min_speed

      # --- MOVE ---
      self.position += forward * speed_now
      self.rect.center = self.position

      # --- ROTATE ---
      self.angle = math.degrees(math.atan2(-forward.y, forward.x)) - 90
      self.image = pygame.transform.rotate(self.original_image, self.angle)
      self.rect = self.image.get_rect(center=self.rect.center)
