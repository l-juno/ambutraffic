import pygame
import json
import argparse
import math
import pygame.gfxdraw as gfxdraw


from classes.route.route_map import build_routes
from classes.traffic_light.light_state import LightState
from classes.traffic_light.traffic_light import TrafficLight
from classes.vehicle import Vehicle
from classes.graph.graph import RoadGraph

SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800

# Global variable to hold node positions
# dictionary of [int, pygame.Vector2]
NODE_POS = None

ROWS = 1
COLS = 1

ROAD_COLOR = (50, 50, 50)
BG_COLOR = (30, 30, 30)

ROAD_THICKNESS = SCREEN_WIDTH // 15

NODE_RADIUS = 4
NODE_COLOR = (80, 160, 255)
TEXT_COLOR = (255, 255, 255)
CENTER_LINE_COLOR = (255, 200, 0)
BLUE = (80, 160, 255)
LINE_WIDTH = 2

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

        16: pygame.Vector2(halfX - offset,           0),
        17: pygame.Vector2(halfX + offset,           0),
        18: pygame.Vector2(SCREEN_WIDTH, halfY - offset),
        19: pygame.Vector2(SCREEN_WIDTH, halfY + offset),
        20: pygame.Vector2(halfX + offset,           SCREEN_HEIGHT),
        21: pygame.Vector2(halfX - offset,           SCREEN_HEIGHT),
        22: pygame.Vector2(0, halfY + offset),
        23: pygame.Vector2(0, halfY - offset),

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

        label = font.render(str(node_id), True, TEXT_COLOR)
        screen.blit(label, (int(pos.x) , int(pos.y)))



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

    # draw_dashed_line(
    #     screen, CENTER_LINE_COLOR,
    #     (cx, 0),
    #     (cx, intersection.top)
    # )

    # draw_dashed_line(
    #     screen, CENTER_LINE_COLOR,
    #     (cx, intersection.bottom),
    #     (cx, SCREEN_HEIGHT)
    # )

    # draw_dashed_line(
    #     screen, CENTER_LINE_COLOR,
    #     (0, cy),
    #     (intersection.left, cy)
    # )

    # draw_dashed_line(
    #     screen, CENTER_LINE_COLOR,
    #     (intersection.right, cy),
    #     (SCREEN_WIDTH, cy)
    # )




def draw_dashed_line(screen, color, start, end, dash_length=20, gap=15, width=1):
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


def draw_arc(surface, center, radius, start_angle, stop_angle, color):
    x, y = int(center[0]), int(center[1])
    r = int(round(radius))

    start_angle = int(round(start_angle % 360))
    stop_angle  = int(round(stop_angle % 360))

    if start_angle == stop_angle:
        gfxdraw.circle(surface, x, y, r, color)
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

def load_from_json(path, routes):
    with open(path, "r") as f:
        data = json.load(f)

    vehicles = []
    for v in data["vehicles"]:
        route_id = v["route"]
        speed = v["speed"]
        vehicle_type = v.get("type")

        if route_id not in routes:
            raise ValueError(f"Unknown route '{route_id}' in scenario file")

        route = routes[route_id]
        vehicles.append(Vehicle(route, speed, vehicle_type))

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
    traffic_lights.append(TrafficLight((NODE_POS[3][0],NODE_POS[3][1]), LightState.EW_RED))
    traffic_lights.append(TrafficLight((NODE_POS[7][0],NODE_POS[7][1]), LightState.EW_RED))
    
    traffic_lights.append(TrafficLight((NODE_POS[1][0],NODE_POS[1][1]), LightState.NS_GREEN))
    traffic_lights.append(TrafficLight((NODE_POS[5][0],NODE_POS[5][1]), LightState.NS_GREEN))
    
    # graph.debug_print()
    routes = build_routes(graph)
    vehicles = load_from_json(args.scenario, routes)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BG_COLOR)
        
        
        draw_roads(screen)
        draw_edges(screen, graph)
        draw_nodes(screen, font)
        
        for tl in traffic_lights:
            tl.draw(screen)
            tl.update()

        for vehicle in vehicles[:]:
            vehicle.update(vehicles)
            if vehicle.finished:
                vehicles.remove(vehicle)
            else:
                screen.blit(vehicle.image, vehicle.rect)



        pygame.display.flip()
        clock.tick(60)

    pygame.quit()



if __name__ == "__main__":
    main()
