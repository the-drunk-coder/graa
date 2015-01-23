"""
Generate specific graph structures

"""

import copy
from graa_structures import *
from graa_session import GraaSession as session
from graa_parser import GraaParser as parser

def circle(size, def_node_tpl, def_edge_tpl):
    "Generate a simple cyclic list"
    # parse templates
    # data is the third element in the tuple the parser returns ...
    def_node = parser.parse(def_node_tpl)[0][2]
    def_edge = parser.parse(def_edge_tpl)[0][2]
    cycle = Graph()
    last_node = None
    for i in range(1,size+1):
        node = copy.deepcopy(def_node)
        node.id = str(i)
        cycle.add_node(node)        
        edge = copy.deepcopy(def_edge)
        edge.dest = node.id        
        if last_node != None:
            edge.source = last_node.id
            cycle.add_edge(edge.source, edge)
        last_node = node
    # tie knot for cycle
    last_edge = copy.deepcopy(def_edge)
    last_edge.dest = str(1)
    last_edge.source = str(size)
    cycle.add_edge(last_edge.source, last_edge)
    cycle_id = def_node.graph_id
    session.graphs[cycle_id] = cycle
    return cycle_id
# end cycle
