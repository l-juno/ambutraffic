# Graph structure to represent roads and intersections as nodes and edges
class RoadGraph:
    def __init__(self):
        self.nodes = {}     
        self.edges = []
        self.adj = {}       # a list of (neighbour_id, edge)

    def add_node(self, node):
        self.nodes[node.id] = node
        self.adj[node.id] = []

    def add_edge(self, edge):
        self.edges.append(edge)
        self.adj[edge.start].append((edge.end, edge))
