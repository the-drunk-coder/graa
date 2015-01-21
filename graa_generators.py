"""
Generate specific graph structures

"""

import copy
from graa_structures import *

class GraaGenerators():
    def generate_cycle(size, def_node, def_edge):
        "Generate a simple cyclic list"
        cycle = Graph()
        last_node = None
        for i in range(1,size+1):
            node = copy.deepcopy(def_node)
            node.id = str(i)
            cycle.add_node(node)
            if last_node != None:
                edge = copy.deepcopy(def_edge)
                edge.dest = node.id
                cycle.add_edge(last_node.id, edge)
                last_node = node
        # tie knot for cycle
        last_edge = copy.deepcopy(def_edge)
        last_edge.dest = str(1)
        cycle.add_edge(str(size), last_edge)
        return cycle

if __name__ == "__main__":
    node = Node("hi", "hello")
    edge = Edge("hi", 1000)
    print(GraaGenerators.generate_cycle(5, node, edge))
