class Edge:
    def __init__(self, start, end, edge_type = "straight"):
        self.start = start
        self.end = end
        self.edge_type = edge_type  # could be 'straight', 'left', 'right'
