class Route:
    def __init__(self, route_id, nodes, edges):
        self.id = route_id
        self.nodes = nodes      
        self.edges = edges      

    def get_start_node(self):
        return self.nodes[0]

    def get_end_node(self):
        return self.nodes[-1]
