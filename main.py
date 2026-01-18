import pygame
import json
import argparse
import math

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

ROAD_THICKNESS = SCREEN_WIDTH // 5

NODE_RADIUS = 4
NODE_COLOR = (200, 0, 0)
TEXT_COLOR = (255, 255, 255)
CENTER_LINE_COLOR = (255, 200, 0)
BLUE = (80, 160, 255)


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

        8: pygame.Vector2(halfX - offset,           0),
        9: pygame.Vector2(halfX + offset,           0),
        10: pygame.Vector2(SCREEN_WIDTH, halfY - offset),
        11: pygame.Vector2(SCREEN_WIDTH, halfY + offset),
        12: pygame.Vector2(halfX + offset,           SCREEN_HEIGHT),
        13: pygame.Vector2(halfX - offset,           SCREEN_HEIGHT),
        14: pygame.Vector2(0, halfY + offset),
        15: pygame.Vector2(0, halfY - offset),

    }


# get position of node by its ID
def getPos(node_id: int) -> pygame.Vector2:
    return NODE_POS[node_id]


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

    draw_dashed_line(
        screen, CENTER_LINE_COLOR,
        (cx, 0),
        (cx, intersection.top)
    )

    draw_dashed_line(
        screen, CENTER_LINE_COLOR,
        (cx, intersection.bottom),
        (cx, SCREEN_HEIGHT)
    )

    draw_dashed_line(
        screen, CENTER_LINE_COLOR,
        (0, cy),
        (intersection.left, cy)
    )

    draw_dashed_line(
        screen, CENTER_LINE_COLOR,
        (intersection.right, cy),
        (SCREEN_WIDTH, cy)
    )



def draw_nodes(screen, font):
    # placeholder nodes for easier visualization for now
    for node_id, pos in NODE_POS.items():
        pygame.draw.circle(screen, NODE_COLOR, (int(pos.x), int(pos.y)), NODE_RADIUS)

        label = font.render(str(node_id), True, TEXT_COLOR)
        screen.blit(label, (int(pos.x) + 10, int(pos.y) - 10))



def get_intersection_rect():
    return pygame.Rect(
        (SCREEN_WIDTH - ROAD_THICKNESS) // 2,
        (SCREEN_HEIGHT - ROAD_THICKNESS) // 2,
        ROAD_THICKNESS,
        ROAD_THICKNESS
    )

def draw_dashed_line(screen, color, start, end, dash_length=20, gap=15, width=4):
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




# def draw_corner_arc(screen, p_start: pygame.Vector2, p_end: pygame.Vector2, turn_type, width=2):
#     # Calculate center of the arc

#     # have right turn and left turn radians
#     # right turn: (pi to pi/2)
#     # left turn: (0 to pi/2)
#     # straight: just line

#     # rectangle for arc is x1




# def draw_edges(screen):
#     draw_corner_arc(screen, getPos(1), getPos(2), BLUE, width=2)

def draw_edges(screen, graph):
    for edge_list in graph.adjacency.values():
        for edge in edge_list:
            start_pos = edge.start.get_pos()
            end_pos = edge.end.get_pos()

            pygame.draw.line(
                screen,
                BLUE,
                (int(start_pos.x), int(start_pos.y)),
                (int(end_pos.x), int(end_pos.y)),
                3
            )


ROAD_THICKNESS = SCREEN_WIDTH // 5

NODE_RADIUS = 4
NODE_COLOR = (200, 0, 0)
TEXT_COLOR = (255, 255, 255)
CENTER_LINE_COLOR = (255, 200, 0)
BLUE = (80, 160, 255)


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

        8: pygame.Vector2(halfX - offset,           0),
        9: pygame.Vector2(halfX + offset,           0),
        10: pygame.Vector2(SCREEN_WIDTH, halfY - offset),
        11: pygame.Vector2(SCREEN_WIDTH, halfY + offset),
        12: pygame.Vector2(halfX + offset,           SCREEN_HEIGHT),
        13: pygame.Vector2(halfX - offset,           SCREEN_HEIGHT),
        14: pygame.Vector2(0, halfY + offset),
        15: pygame.Vector2(0, halfY - offset),

    }


# get position of node by its ID
def getPos(node_id: int) -> pygame.Vector2:
    return NODE_POS[node_id]


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

    draw_dashed_line(
        screen, CENTER_LINE_COLOR,
        (cx, 0),
        (cx, intersection.top)
    )

    draw_dashed_line(
        screen, CENTER_LINE_COLOR,
        (cx, intersection.bottom),
        (cx, SCREEN_HEIGHT)
    )

    draw_dashed_line(
        screen, CENTER_LINE_COLOR,
        (0, cy),
        (intersection.left, cy)
    )

    draw_dashed_line(
        screen, CENTER_LINE_COLOR,
        (intersection.right, cy),
        (SCREEN_WIDTH, cy)
    )



def draw_nodes(screen, font):
    # placeholder nodes for easier visualization for now
    for node_id, pos in NODE_POS.items():
        pygame.draw.circle(screen, NODE_COLOR, (int(pos.x), int(pos.y)), NODE_RADIUS)

        label = font.render(str(node_id), True, TEXT_COLOR)
        screen.blit(label, (int(pos.x) + 10, int(pos.y) - 10))



def get_intersection_rect():
    return pygame.Rect(
        (SCREEN_WIDTH - ROAD_THICKNESS) // 2,
        (SCREEN_HEIGHT - ROAD_THICKNESS) // 2,
        ROAD_THICKNESS,
        ROAD_THICKNESS
    )

def draw_dashed_line(screen, color, start, end, dash_length=20, gap=15, width=4):
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




# def draw_corner_arc(screen, p_start: pygame.Vector2, p_end: pygame.Vector2, turn_type, width=2):
#     # Calculate center of the arc

#     # have right turn and left turn radians
#     # right turn: (pi to pi/2)
#     # left turn: (0 to pi/2)
#     # straight: just line

#     # rectangle for arc is x1




# def draw_edges(screen):
#     draw_corner_arc(screen, getPos(1), getPos(2), BLUE, width=2)


def load_from_json(path):
    with open(path, "r") as f:
        data = json.load(f)

    vehicles = []
    for v in data["vehicles"]:
        position = pygame.Vector2(v["position"][0], v["position"][1])
        speed = v["speed"]
        vehicle_type = v.get("type")

        vehicles.append(Vehicle(position, speed, vehicle_type))

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
    vehicles = load_from_json(args.scenario)
    font = pygame.font.SysFont(None, 24)
    global NODE_POS
    NODE_POS = build_node_positions()
    graph = RoadGraph(NODE_POS)
    graph.debug_print()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(BG_COLOR)
        
        
        draw_roads(screen)
        draw_edges(screen, graph)
        draw_nodes(screen, font)
        
        for vehicle in vehicles:
            screen.blit(vehicle.image, vehicle.rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()



if __name__ == "__main__":
    main()
