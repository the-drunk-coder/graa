"""
Generate specific graph structures

"""

import copy
from graa_structures import *
from graa_session import GraaSession as session
from graa_parser import GraaParser as parser

def circle(size, def_node_tpl, def_edge_tpl):
    """Generate a simple cyclic list"""
    # parse templates
    # data is the third element in the tuple the parser returns ...
    def_node = parser.parse(def_node_tpl)[0][2]
    def_edge = parser.parse(def_edge_tpl)[0][2]
    cycle = Graph()
    last_node = None
    for i in range(1,size+1):
        node = copy.deepcopy(def_node)
        node.id = i
        cycle.add_node(node)        
        edge = copy.deepcopy(def_edge)
        edge.dest = node.id        
        if last_node != None:
            edge.source = last_node.id
            cycle.add_edge(edge.source, edge)
        last_node = node
    # tie knot for cycle
    last_edge = copy.deepcopy(def_edge)
    last_edge.dest = 1
    last_edge.source = size
    cycle.add_edge(last_edge.source, last_edge)
    cycle_id = def_node.graph_id
    session.graphs[cycle_id] = cycle
    return cycle_id
# end cycle


def star(size, def_node_tpl, def_edge_tpl):
    """Generate a star graph."""
    # parse templates
    # data is the third element in the tuple the parser returns ...
    def_node = parser.parse(def_node_tpl)[0][2]
    def_edge = parser.parse(def_edge_tpl)[0][2]
    star = Graph()
    center_node = copy.deepcopy(def_node)
    center_node.id = 1
    star.add_node(center_node)
    for i in range(2,size+1):       
        node = copy.deepcopy(def_node)
        node.id = i
        star.add_node(node)
        in_edge = copy.deepcopy(def_edge)
        in_edge.source = center_node.id
        in_edge.dest = node.id        
        star.add_edge(in_edge.source, in_edge)
        out_edge = copy.deepcopy(def_edge)
        out_edge.source = node.id
        out_edge.dest = center_node.id        
        star.add_edge(out_edge.source, out_edge)                
    star_id = def_node.graph_id
    session.graphs[star_id] = star
    return star_id
# end star


def grid(xsize, ysize, def_node_tpl, def_edge_tpl):
    """ Generate a grid of type of size x*y"""
    def_node = parser.parse(def_node_tpl)[0][2]
    def_edge = parser.parse(def_edge_tpl)[0][2]
    overall_size = xsize * ysize
    grid = Graph()
    # generate nodes
    for i in range(1, overall_size + 1):
        node = copy.deepcopy(def_node)
        node.id = i
        grid.add_node(node)
    # generate edges
    for i in range(1, overall_size):
        if i % xsize != 0:
            edge = copy.deepcopy(def_edge)
            edge.source = i
            edge.dest = i + 1        
            grid.add_edge(edge.source, edge)
        if i + xsize <= overall_size:
            edge = copy.deepcopy(def_edge)
            edge.source = i
            edge.dest = i + xsize        
            grid.add_edge(edge.source, edge)
    # last edge
    edge = copy.deepcopy(def_edge)
    edge.source = overall_size
    edge.dest = 1        
    grid.add_edge(edge.source, edge)
    grid_id = def_node.graph_id
    session.graphs[grid_id] = grid
    return grid_id
# end grid
