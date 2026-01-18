from classes.route.route import Route

def build_routes(graph):
    routes = {}

    # North
    routes["N_straight"] = build_route(graph, "N_straight", [16, 8, 0, 5, 13, 21])
    routes["N_right"]    = build_route(graph, "N_right",    [16, 8, 0, 7, 15, 23])
    routes["N_left"]     = build_route(graph, "N_left",     [16, 8, 24, 3, 11, 19])

    # East
    routes["E_straight"] = build_route(graph, "E_straight", [18, 10, 2, 7, 15, 23])
    routes["E_right"]    = build_route(graph, "E_right",    [18, 10, 2, 1, 9, 17])
    routes["E_left"]     = build_route(graph, "E_left",     [18, 10, 25, 5, 13, 21])

    # South
    routes["S_straight"] = build_route(graph, "S_straight", [20, 12, 4, 1, 9, 17])
    routes["S_right"]    = build_route(graph, "S_right",    [20, 12, 4, 3, 11, 19])
    routes["S_left"]     = build_route(graph, "S_left",     [20, 12, 26, 7, 15, 23])

    # West
    routes["W_straight"] = build_route(graph, "W_straight", [22, 14, 6, 3, 11, 19])
    routes["W_right"]    = build_route(graph, "W_right",    [22, 14, 6, 5, 13, 21])
    routes["W_left"]     = build_route(graph, "W_left",     [22, 14, 27, 1, 9, 17])

    return routes



def build_route(graph, route_id, node_ids):
    nodes = [graph.nodes[id] for id in node_ids]
    edges = []

    for i in range(len(node_ids) - 1):
        edge = graph.get_edge(node_ids[i], node_ids[i+1])
        if edge is None:
            raise ValueError(f"No edge between node {node_ids[i]} and {node_ids[i+1]}")
        edges.append(edge)


    route = Route(route_id, nodes, edges)
    route.path = build_path_from_edges(edges, steps=25)
    return route

    
    # return Route(route_id, nodes, edges)


import math
import pygame

def sample_arc(center, radius, start_rad, end_rad, steps=25):
    pts = []
    if end_rad < start_rad:
        end_rad += 2 * math.pi
    for i in range(steps + 1):
        t = i / steps
        ang = start_rad + (end_rad - start_rad) * t
        pts.append(pygame.Vector2(
            center.x + radius * math.cos(ang),
            center.y + radius * math.sin(ang)
        ))
    return pts

def sample_quadratic_bezier(p0, p1, p2, steps=25):
    pts = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        pts.append((u*u)*p0 + (2*u*t)*p1 + (t*t)*p2)
    return pts

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

def right_turn_points(start, end, radius, steps=25):
    direction = get_right_turn_direction(start, end)

    if direction == "NW":
        center = pygame.Vector2(end.x, start.y)
        start_angle = 0
        end_angle   = 0.5 * math.pi

    elif direction == "EN":
        center = pygame.Vector2(start.x, end.y)
        start_angle = 0.5 * math.pi
        end_angle   = math.pi

    elif direction == "SE":
        center = pygame.Vector2(end.x, start.y)
        start_angle = math.pi
        end_angle   = 1.5 * math.pi

    elif direction == "WS":
        center = pygame.Vector2(start.x, end.y)
        start_angle = 1.5 * math.pi
        end_angle   = 0

    else:
        return [start, end]

    return sample_arc(center, radius, start_angle, end_angle, steps)


def edge_to_points(edge, steps=25):
    start = edge.start.get_pos()
    end = edge.end.get_pos()

    if edge.edge_type == "straight":
        return [start, end]

    if edge.edge_type == "right":
        start = edge.start.get_pos()
        end   = edge.end.get_pos()

        # IMPORTANT: match your radius choice (you used abs(dx))
        radius = int(abs(end.x - start.x))

        return right_turn_points(start, end, radius, steps=steps)


    if edge.edge_type == "left":
        # reuse your bezier “feel”
        move = end - start
        if move.length() == 0:
            return [start]
        direction = move.normalize()
        perp = pygame.Vector2(-direction.y, direction.x)
        ctrl = start + direction * 40 + perp * 30

        return sample_quadratic_bezier(start, ctrl, end, steps)

    return [start, end]

def build_path_from_edges(edges, steps=25):
    path = []
    for e in edges:
        pts = edge_to_points(e, steps=steps)
        if path and pts:
            pts = pts[1:]  # avoid duplicates between edges
        path.extend(pts)
    return path


