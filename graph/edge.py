from dataclasses import dataclass

@dataclass
class Edge:
    start: int
    end: int
    length: float
    congession: float = 0.0
    priority: int = 0