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

    return Route(route_id, nodes, edges)

