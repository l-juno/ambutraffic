import pygame
import json
import argparse
import math
import random
import pygame.gfxdraw as gfxdraw


from classes.route.route_map import build_routes
from classes.traffic_light.light_state import LightState
from classes.traffic_light.traffic_light import TrafficLight
from classes.vehicle import Vehicle
from classes.graph.graph import RoadGraph

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

ROUTE_TO_TRAFFIC_LIGHT = {
    "N_straight": 3, "N_right": 3, "N_left": 3,
    "S_straight": 2, "S_right": 2, "S_left": 2,
    "E_straight": 1, "E_right": 1, "E_left": 1,
    "W_straight": 0, "W_right": 0, "W_left": 0,
}


class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.font = pygame.font.SysFont(None, 24)
    
    def draw(self, screen):
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=5)
        
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
    
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
    
    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False


def spawn_vehicle(vehicle_type, routes, traffic_lights):
    """Spawn a new vehicle on a random route."""
    route_names = list(routes.keys())
    route_name = random.choice(route_names)
    route = routes[route_name]
    traffic_light_index = ROUTE_TO_TRAFFIC_LIGHT[route_name]
    speed = 2 if vehicle_type == "ambulance" else 3
    return Vehicle(route, speed, vehicle_type, traffic_lights[traffic_light_index])


# Global variable to hold node positions
# dictionary of [int, pygame.Vector2]
NODE_POS = None

ROWS = 1
COLS = 1

ROAD_COLOR = (50, 50, 50)
BG_COLOR = (30, 30, 30)

ROAD_THICKNESS = SCREEN_WIDTH // 10

NODE_RADIUS = 4
NODE_COLOR = (80, 160, 255)
TEXT_COLOR = (255, 255, 255)
YELLOW = (255, 200, 0)
BLUE = (80, 160, 255)
RED = (255, 80, 80)
GREEN = (80, 255, 80)
WHITE = (255, 255, 255)
LINE_WIDTH = 2
ZONE_COLOR = (255, 80, 80)
AMBULANCE_ZONE_RADIUS = 300
TRAFFIC_ZONE_RADIUS = 200
ZONE_WIDTH = 2



def build_node_positions():
    halfX = SCREEN_WIDTH // 2
    halfY = SCREEN_HEIGHT // 2
    halfRoad = ROAD_THICKNESS // 2
    offset = ROAD_THICKNESS // 4

    return {
        0: pygame.Vector2(halfX - offset,           halfY - (halfRoad + offset)),
        1: pygame.Vector2(halfX + offset,           halfY - (halfRoad + offset)),
        2: pygame.Vector2(halfX + (halfRoad+offset), halfY - offset),
        3: pygame.Vector2(halfX + (halfRoad+offset), halfY + offset),
        4: pygame.Vector2(halfX + offset,           halfY + (halfRoad + offset)),
        5: pygame.Vector2(halfX - offset,           halfY + (halfRoad + offset)),
        6: pygame.Vector2(halfX - (halfRoad+offset), halfY + offset),
        7: pygame.Vector2(halfX - (halfRoad+offset), halfY - offset),

        8: pygame.Vector2(halfX - offset,           halfY - (4*halfRoad + offset)),
        9: pygame.Vector2(halfX + offset,           halfY - (4*halfRoad + offset)),
        10: pygame.Vector2(halfX + (4*halfRoad+offset), halfY - offset),
        11: pygame.Vector2(halfX + (4*halfRoad+offset), halfY + offset),
        12: pygame.Vector2(halfX + offset,           halfY + (4*halfRoad + offset)),
        13: pygame.Vector2(halfX - offset,           halfY + (4*halfRoad + offset)),
        14: pygame.Vector2(halfX - (4*halfRoad+offset), halfY + offset),
        15: pygame.Vector2(halfX - (4*halfRoad+offset), halfY - offset),

        16: pygame.Vector2(halfX - offset,           0 - offset),
        17: pygame.Vector2(halfX + offset,           0 - offset),
        18: pygame.Vector2(SCREEN_WIDTH + offset, halfY - offset),
        19: pygame.Vector2(SCREEN_WIDTH + offset, halfY + offset),
        20: pygame.Vector2(halfX + offset,           SCREEN_HEIGHT + offset),
        21: pygame.Vector2(halfX - offset,           SCREEN_HEIGHT + offset),
        22: pygame.Vector2(0 - offset, halfY + offset),
        23: pygame.Vector2(0 - offset, halfY - offset),

        24: pygame.Vector2(halfX,           halfY - (halfRoad + offset)),
        25: pygame.Vector2(halfX + (halfRoad+offset), halfY),
        26: pygame.Vector2(halfX,           halfY + (halfRoad + offset)),
        27: pygame.Vector2(halfX - (halfRoad+offset), halfY),
    }


# get position of node by its ID
def getPos(node_id: int) -> pygame.Vector2:
    return NODE_POS[node_id]


def draw_nodes(screen, font):
    # placeholder nodes for easier visualization for now
    for node_id, pos in NODE_POS.items():
        pygame.draw.circle(screen, NODE_COLOR, (int(pos.x), int(pos.y)), NODE_RADIUS)

        # label = font.render(str(node_id), True, TEXT_COLOR)
        # screen.blit(label, (int(pos.x) , int(pos.y)))
        
def draw_vehicle_stats(screen, vehicles):
    font = pygame.font.SysFont(None, 18)

    line_height = 18
    x = 560
    y = 460

    for i, v in enumerate(vehicles):
        text_str = (
            f"V{i} | {v.type} | "
            f"Pos=({v.position.x:.1f},{v.position.y:.1f}) | "
            f"Speed={v.speed:.2f} | "
            f"Angle={v.angle:.1f}"
        )

        text = font.render(text_str, True, (255, 255, 255))
        screen.blit(text, (x, y))
        y += line_height





def get_intersection_rect():
    return pygame.Rect(
        (SCREEN_WIDTH - ROAD_THICKNESS) // 2,
        (SCREEN_HEIGHT - ROAD_THICKNESS) // 2,
        ROAD_THICKNESS,
        ROAD_THICKNESS
    )


def draw_roads(screen):
    v_road = pygame.Rect(
        (SCREEN_WIDTH - ROAD_THICKNESS) // 2,
        0,
        ROAD_THICKNESS,
        SCREEN_HEIGHT
    )
    h_road = pygame.Rect(
        0,
        (SCREEN_HEIGHT - ROAD_THICKNESS) // 2,
        SCREEN_WIDTH,
        ROAD_THICKNESS
    )

    pygame.draw.rect(screen, ROAD_COLOR, v_road)
    pygame.draw.rect(screen, ROAD_COLOR, h_road)

    intersection = get_intersection_rect()

    cx = SCREEN_WIDTH // 2
    cy = SCREEN_HEIGHT // 2
    stoplineLength = ROAD_THICKNESS // 2

    offsetRoad = 1 * ROAD_THICKNESS // 8

    draw_dashed_line(
        screen, YELLOW,
        (cx+offsetRoad, 0),
        (cx+offsetRoad, intersection.top - 20)
    )

    pygame.draw.line(
        screen,
        (255, 255, 255),
        (cx+offsetRoad, intersection.top - 20),
        (cx+offsetRoad - stoplineLength, intersection.top - 20) , 
        2
    )

    draw_dashed_line_same_lane(
        screen, WHITE,
        (cx-offsetRoad, 0),
        (cx-offsetRoad, intersection.top-20)
    )

    draw_dashed_line(
        screen, YELLOW,
        (cx-offsetRoad, intersection.bottom + 20),
        (cx-offsetRoad, SCREEN_HEIGHT)
    )

    pygame.draw.line(
        screen,
        (255, 255, 255),
        (cx-offsetRoad, intersection.bottom + 20),
        (cx-offsetRoad + stoplineLength, intersection.bottom + 20), 
        2
    )

    draw_dashed_line_same_lane(
        screen, WHITE,
        (cx+offsetRoad, intersection.bottom + 20),
        (cx+offsetRoad, SCREEN_HEIGHT)
    )

    draw_dashed_line(
        screen, YELLOW,
        (0, cy-offsetRoad),
        (intersection.left - 20, cy-offsetRoad)
    )

    pygame.draw.line(
        screen,
        (255, 255, 255),
        (intersection.left - 20, cy-offsetRoad),
        (intersection.left - 20, cy-offsetRoad + stoplineLength), 
        2
    )

    draw_dashed_line_same_lane(
        screen, WHITE,
        (0, cy+offsetRoad),
        (intersection.left - 20, cy+offsetRoad)
    )

    draw_dashed_line(
        screen, YELLOW,
        (intersection.right + 20, cy+offsetRoad),
        (SCREEN_WIDTH, cy+offsetRoad)
    )
    pygame.draw.line(
        screen,
        (255, 255, 255),
        (intersection.right + 20, cy+offsetRoad),
        (intersection.right + 20, cy+offsetRoad - stoplineLength), 
        2
    )

    draw_dashed_line_same_lane(
        screen, WHITE,
        (intersection.right + 20, cy-offsetRoad),
        (SCREEN_WIDTH, cy-offsetRoad)
    )




def draw_dashed_line(screen, color, start, end, dash_length=20, gap=0, width=1):
    x1, y1 = start
    x2, y2 = end

    length = ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
    dx = (x2 - x1) / length
    dy = (y2 - y1) / length

    dist = 0
    while dist < length:
        dash_end = min(dist + dash_length, length)
        sx = x1 + dx * dist
        sy = y1 + dy * dist
        ex = x1 + dx * dash_end
        ey = y1 + dy * dash_end
        pygame.draw.line(screen, color, (sx, sy), (ex, ey), width)
        dist += dash_length + gap

def draw_dashed_line_same_lane(screen, color, start, end, dash_length=20, gap=15, width=1):
    x1, y1 = start
    x2, y2 = end

    length = ((x2 - x1)**2 + (y2 - y1)**2) ** 0.5
    dx = (x2 - x1) / length
    dy = (y2 - y1) / length

    dist = 0
    while dist < length:
        dash_end = min(dist + dash_length, length)
        sx = x1 + dx * dist
        sy = y1 + dy * dist
        ex = x1 + dx * dash_end
        ey = y1 + dy * dash_end
        pygame.draw.line(screen, color, (sx, sy), (ex, ey), width)
        dist += dash_length + gap



def draw_left_turn(screen, start: pygame.Vector2, end: pygame.Vector2, turn_type: str,
                     width=LINE_WIDTH, color=(100, 220, 255)):
    direction = end - start
    direction.normalize_ip()

    perp = pygame.Vector2(-direction.y, direction.x)
    if turn_type == "right":
        perp = -perp

    # Control points for quadratic Bezier
    ctrl1 = start + direction * 40 + perp * 30

    steps = 30
    for i in range(steps):
        t = i / steps
        t2 = 1 - t
        pos = (t2 * t2 * start +
               2 * t * t2 * ctrl1 +
               t * t * end)
        next_t = (i + 1) / steps
        next_t2 = 1 - next_t
        next_pos = (next_t2 * next_t2 * start +
                    2 * next_t * next_t2 * ctrl1 +
                    next_t * next_t * end)
        pygame.draw.line(screen, BLUE, pos, next_pos, width)


# def draw_arc(surface, center, radius, start_angle, stop_angle, color):
#     x, y = int(center[0]), int(center[1])
#     r = int(round(radius))

#     start_angle = int(round(start_angle % 360))
#     stop_angle  = int(round(stop_angle % 360))

#     if start_angle == stop_angle:
#         gfxdraw.circle(surface, x, y, r, color)
#     else:
#         gfxdraw.arc(surface, x, y, r, start_angle, stop_angle, color)


def draw_arc(surface, center, radius, start_angle, stop_angle, color):
    x, y = int(center[0]), int(center[1])
    r = int(round(radius))

    start_angle = int(round(start_angle)) % 360
    stop_angle  = int(round(stop_angle)) % 360
    if stop_angle < start_angle:
        gfxdraw.arc(surface, x, y, r, start_angle, 359, color)
        gfxdraw.arc(surface, x, y, r, 0, stop_angle, color)
    elif stop_angle == start_angle:
        gfxdraw.arc(surface, x, y, r, start_angle, (start_angle + 1) % 360, color)
    else:
        gfxdraw.arc(surface, x, y, r, start_angle, stop_angle, color)


# def draw_right_turn(screen, color, start_pos, end_pos, radius, width=LINE_WIDTH):
#     direction = get_right_turn_direction(start_pos, end_pos)

#     if direction == "NW":
#         center = pygame.Vector2(end_pos.x, start_pos.y)
#         start_angle = 1.5 * math.pi 
#         end_angle   = 0 

#     elif direction == "EN":
#         center = pygame.Vector2(start_pos.x, end_pos.y)
#         start_angle = math.pi       
#         end_angle   = 1.5 * math.pi  

#     elif direction == "SE": 
#         center = pygame.Vector2(end_pos.x, start_pos.y)
#         start_angle = 0.5 * math.pi   
#         end_angle   = math.pi 

#     elif direction == "WS": 
#         center = pygame.Vector2(start_pos.x, end_pos.y)
#         start_angle = 0    
#         end_angle   = 0.5 * math.pi  

#     else:
#         return

#     rect = pygame.Rect(center.x - radius, center.y - radius, radius * 2, radius * 2)

#     pygame.draw.arc(screen, color, rect, start_angle, end_angle, width)




def draw_right_turn(screen, color, start_pos, end_pos, radius, width=LINE_WIDTH):
    direction = get_right_turn_direction(start_pos, end_pos)

    if direction == "NW":
        center = pygame.Vector2(end_pos.x, start_pos.y)
        start_angle = 0
        end_angle   = 0.5 * math.pi

    elif direction == "EN":
        center = pygame.Vector2(start_pos.x, end_pos.y)
        start_angle = 0.5 * math.pi
        end_angle   = math.pi

    elif direction == "SE":
        center = pygame.Vector2(end_pos.x, start_pos.y)
        start_angle = math.pi
        end_angle   = 1.5 * math.pi

    elif direction == "WS":
        center = pygame.Vector2(start_pos.x, end_pos.y)
        start_angle = 1.5 * math.pi
        end_angle   = 0

    else:
        return

    # Convert radians -> degrees for gfxdraw
    start_deg = math.degrees(start_angle)
    end_deg   = math.degrees(end_angle)

    # # Draw "thick" arc by drawing multiple 1px arcs around the radius
    # half = max(0, width // 2)
    # for dr in range(-half, half + 1):
    #     draw_arc(screen, center, radius + dr, start_deg, end_deg, color)
    draw_arc(screen, center, radius, start_deg, end_deg, color)




def get_right_turn_direction(start_pos, end_pos):
    direction = ""
    if end_pos.x > start_pos.x and end_pos.y > start_pos.y:
        direction = "WS"
    elif end_pos.x < start_pos.x and end_pos.y > start_pos.y:
        direction = "NW"
    elif end_pos.x > start_pos.x and end_pos.y < start_pos.y:
        direction = "SE"
    elif end_pos.x < start_pos.x and end_pos.y < start_pos.y:
        direction = "EN"

    return direction


def draw_edges(screen, graph):
    for edge_list in graph.adjacency.values():
        for edge in edge_list:
            start_pos = edge.start.get_pos()
            end_pos = edge.end.get_pos()

            if edge.edge_type == "left":
                draw_left_turn(screen, start_pos, end_pos, edge.edge_type)
            elif edge.edge_type == "right":
                radius = abs(end_pos.x - start_pos.x)
                draw_right_turn(screen, BLUE, start_pos, end_pos, radius, width=LINE_WIDTH)
            else:
                pygame.draw.line(
                    screen,
                    BLUE,
                    (int(start_pos.x), int(start_pos.y)),
                    (int(end_pos.x), int(end_pos.y)),
                    LINE_WIDTH
                )

def load_from_json(path, routes, traffic_lights):
    with open(path, "r") as f:
        data = json.load(f)

    vehicles = []
    for v in data["vehicles"]:
        route_id = v["route"]
        speed = v["speed"]
        vehicle_type = v.get("type")
        traffic_light_index = v.get("traffic_light_index")

        if route_id not in routes:
            raise ValueError(f"Unknown route '{route_id}' in scenario file")

        route = routes[route_id]
        vehicles.append(Vehicle(route, speed, vehicle_type, traffic_lights[traffic_light_index]))

    return vehicles

def parse_args():
    parser = argparse.ArgumentParser(description="Ambulance Traffic Simulator")
    parser.add_argument(
        "--scenario",
        type=str,
        required=True,
        help="Path to scenario JSON file"
    )
    return parser.parse_args()

def draw_detection_zone(screen):
    pygame.draw.circle(
        screen,
        RED,
        (SCREEN_WIDTH//2, SCREEN_HEIGHT//2),
        AMBULANCE_ZONE_RADIUS,
        ZONE_WIDTH
    )

    pygame.draw.circle(
        screen,
        YELLOW,
        (SCREEN_WIDTH//2, SCREEN_HEIGHT//2),
        TRAFFIC_ZONE_RADIUS,
        1
    )

def main():
    args = parse_args()

    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 24)

    global NODE_POS
    NODE_POS = build_node_positions()
    graph = RoadGraph(NODE_POS)
    graph.debug_print()

    traffic_lights = []
    traffic_lights.append(
        TrafficLight(pygame.Vector2(NODE_POS[3][0], NODE_POS[3][1]), LightState.EW_GREEN, 3)
    )
    traffic_lights.append(
        TrafficLight(pygame.Vector2(NODE_POS[7][0], NODE_POS[7][1]), LightState.EW_GREEN, 0)
    )
    traffic_lights.append(
        TrafficLight(pygame.Vector2(NODE_POS[1][0], NODE_POS[1][1]), LightState.NS_RED, 1)
    )
    traffic_lights.append(
        TrafficLight(pygame.Vector2(NODE_POS[5][0], NODE_POS[5][1]), LightState.NS_RED, 2)
    )

    routes = build_routes(graph)

    # initial load
    vehicles = load_from_json(args.scenario, routes, traffic_lights)
    ambulance_queue = []

    paused = False
    pause_font = pygame.font.SysFont(None, 36)

    # Create UI buttons
    button_width = 120
    button_height = 40
    button_margin = 10
    button_y = SCREEN_HEIGHT - button_height - button_margin
    
    add_car_btn = Button(
        button_margin, button_y, button_width, button_height,
        "Add Car", (60, 60, 60), (100, 100, 100)
    )
    add_ambulance_btn = Button(
        button_margin + button_width + button_margin, button_y, button_width + 20, button_height,
        "Add Ambulance", (180, 60, 60), (220, 80, 80)
    )

    toggle_lines_btn = Button(
        button_margin + 2* (button_margin + button_width + button_margin), button_y,
        button_width + 20, button_height,
        "Show Lines", (60, 120, 180), (80, 160, 220)
    )
    show_lines = True


    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()
        add_car_btn.update(mouse_pos)
        add_ambulance_btn.update(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif add_car_btn.is_clicked(event):
                new_vehicle = spawn_vehicle("car", routes, traffic_lights)
                vehicles.append(new_vehicle)

            elif add_ambulance_btn.is_clicked(event):
                new_vehicle = spawn_vehicle("ambulance", routes, traffic_lights)
                vehicles.append(new_vehicle)

            elif toggle_lines_btn.is_clicked(event):
                show_lines = not show_lines
                toggle_lines_btn.text = "Hide Lines" if show_lines else "Show Lines"


            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused

                elif event.key == pygame.K_r:
                    paused = False
                    vehicles = load_from_json(args.scenario, routes, traffic_lights)
                    ambulance_queue = [] 

        screen.fill(BG_COLOR)
        draw_roads(screen)
        if show_lines:
            draw_edges(screen, graph)
            draw_nodes(screen, font)
            draw_detection_zone(screen)
        draw_vehicle_stats(screen, vehicles)

        if not paused:
            traffic_lights[0].update()

            # Update all vehicles
            for vehicle in vehicles[:]:
                vehicle.update(vehicles)
                if vehicle.finished:
                    vehicles.remove(vehicle)

        for vehicle in vehicles:
            if vehicle.type == "ambulance":
                if vehicle.isInAmbulanceZone and vehicle not in ambulance_queue:
                    ambulance_queue.append(vehicle)
                elif not vehicle.isInAmbulanceZone and vehicle in ambulance_queue:
                    ambulance_queue.remove(vehicle)
        ambulance_queue = [v for v in ambulance_queue if v in vehicles]

        # Check if any ambulance is in zone
        ambulance_in_zone = any(v.isInAmbulanceZone and v.type == "ambulance" for v in vehicles)

        # Apply ambulance priority OR sync lights properly
        if ambulance_queue and ambulance_in_zone:
            priority_ambulance = ambulance_queue[0]
            ambulance_tl_id = priority_ambulance.traffic_light.id
            for tl in traffic_lights:
                if tl.id == ambulance_tl_id:
                    # Give green to ambulance's direction
                    tl.state = LightState.NS_GREEN if tl.id in (1, 2) else LightState.EW_GREEN
                else:
                    # Give red to other directions
                    tl.state = LightState.NS_RED if tl.id in (1, 2) else LightState.EW_RED
        else:
            # Sync all lights based on master light (traffic_lights[0])
            master_state = traffic_lights[0].state
            
            # E/W pair (traffic_lights[0] and [1]) - same state
            traffic_lights[1].state = master_state
            traffic_lights[1].timer = traffic_lights[0].timer
            
            # N/S pair (traffic_lights[2] and [3]) - opposite state
            # When E/W is green/yellow, N/S is red
            # When E/W is red, N/S is green
            if master_state == LightState.EW_GREEN:
                opposite_state = LightState.NS_RED
            elif master_state == LightState.EW_YELLOW:
                opposite_state = LightState.NS_RED
            elif master_state == LightState.EW_RED:
                opposite_state = LightState.NS_GREEN
            elif master_state == LightState.NS_GREEN:
                opposite_state = LightState.EW_RED
            elif master_state == LightState.NS_YELLOW:
                opposite_state = LightState.EW_RED
            else:  # NS_RED
                opposite_state = LightState.EW_GREEN
            
            traffic_lights[2].state = opposite_state
            traffic_lights[3].state = opposite_state
            traffic_lights[2].timer = traffic_lights[0].timer
            traffic_lights[3].timer = traffic_lights[0].timer

        for tl in traffic_lights:
            tl.draw(screen)

        # Draw ambulance zone indicator if ambulance is present
        if ambulance_in_zone and show_lines:
            pygame.draw.circle(
                screen,
                GREEN,
                (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2),
                AMBULANCE_ZONE_RADIUS,
                ZONE_WIDTH
            )

        # Draw all vehicles
        for vehicle in vehicles:
            screen.blit(vehicle.image, vehicle.rect)

        if paused:
            text = pause_font.render(
                "PAUSED (Space = resume, R = reset)",
                True,
                (255, 255, 255)
            )
            screen.blit(text, (20, 20))
        else:
            text = pause_font.render(
                "Press SPACE to pause, R to reset scenario",
                True,
                (255, 255, 255)
            )
            screen.blit(text, (20, 20))

        # Draw UI buttons
        add_car_btn.draw(screen)
        add_ambulance_btn.draw(screen)
        toggle_lines_btn.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
