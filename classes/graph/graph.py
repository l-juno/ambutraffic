# Graph structure to represent roads and intersections as nodes and edges
from classes.graph.node import Node
from classes.graph.edge import Edge

class RoadGraph:
    def __init__(self, node_coords):
        self.nodes = {}         # list of Nodes
        self.edges = []         # list of Edges
        self.adjacency = {}    # list of outgoing Edge
        self.build_intersection(node_coords)

    def build_intersection(self, node_coords):
        # Create all nodes 
        for node_id, position in node_coords.items():
            self.add_node(Node(node_id, position.x, position.y))

        # Create edges to connect nodes at an intersection
        # Straight connections
        self.add_edge(0, 5, edge_type="straight") # from N_in to S_out
        self.add_edge(2, 7, edge_type="straight") # from E_in to W_out
        self.add_edge(4, 1, edge_type="straight") # from S_in to N_out
        self.add_edge(6, 3, edge_type="straight") # from W_in to E_out

        # Right turns
        self.add_edge(0, 7, edge_type="right") # from N_in to W_out
        self.add_edge(2, 1, edge_type="right") # from E_in to N_out
        self.add_edge(4, 3, edge_type="right") # from S_in to E_out
        self.add_edge(6, 5, edge_type="right") # from W_in to S_out

        # Left turns
        self.add_edge(8, 24, edge_type="approach") # merge to left turn lane
        self.add_edge(10, 25, edge_type="approach")
        self.add_edge(12, 26, edge_type="approach")
        self.add_edge(14, 27, edge_type="approach")

        self.add_edge(24, 3, edge_type="left") # from N_in to E_out
        self.add_edge(25, 5, edge_type="left") # from E_in to S_out
        self.add_edge(26, 7, edge_type="left") # from S_in to W_out
        self.add_edge(27, 1, edge_type="left") # from W_in to N_out

        # Road → Entry
        self.add_edge(16, 8, edge_type="approach")
        self.add_edge(18, 10, edge_type="approach")
        self.add_edge(20, 12, edge_type="approach")
        self.add_edge(22, 14, edge_type="approach")

        self.add_edge(8, 0, edge_type="approach") 
        self.add_edge(12, 4, edge_type="approach")
        self.add_edge(14, 6, edge_type="approach")
        self.add_edge(10, 2, edge_type="approach")

        # Exit → Road
        self.add_edge(1, 9, edge_type="exit")
        self.add_edge(5, 13, edge_type="exit")
        self.add_edge(3, 11, edge_type="exit")
        self.add_edge(7, 15, edge_type="exit")

        self.add_edge(9, 17, edge_type="exit")
        self.add_edge(11, 19, edge_type="exit")
        self.add_edge(13, 21, edge_type="exit")
        self.add_edge(15, 23, edge_type="exit")


    def add_node(self, node):
        self.nodes[node.id] = node
        self.adjacency[node.id] = []

    def add_edge(self, from_id, to_id, edge_type="straight"):
        edge = Edge(self.nodes[from_id], self.nodes[to_id], edge_type)
        self.adjacency[from_id].append(edge)
        self.edges.append(edge)

    def get_edge(self, from_id, to_id):
        for edge in self.adjacency[from_id]:
            if edge.end.id == to_id:
                return edge
        return None

    def debug_print(self):
        print("=== ROAD GRAPH DEBUG ===")
        for node_id, edges in self.adjacency.items():
            node = self.nodes[node_id]
            print(f"Node {node_id} at {node.get_pos()}:")
            for edge in edges:
                print(
                    f"  -> {edge.end.id} "
                    f"(type={edge.edge_type})"
                )



