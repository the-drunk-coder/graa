from graa_structures import *
from graa_base import *
from graa_parser import GraaParser as parser
from graa_logger import GraaLogger as log

"""
Dispatch parser output to session

"""
class GraaDispatcher():            
    def __init__(self):
       self.dispatcher_map = {}
       self.dispatcher_map[parser.NODE] = self.dispatch_node       
       self.dispatcher_map[parser.EDGE] = self.dispatch_edge
       self.dispatcher_map[parser.DELETE] = self.dispatch_deletion        
    # The main dispatcher function, bridge between parser and code execution
    def dispatch(self, parser_output):
        elem = parser_output[0]
        try:
            self.dispatcher_map[elem[0]](*elem[1:])
        except KeyError:
            log.action("Can't dispatch '{}', no dispatcher present!".format(elem))
        except DispatcherError as de:
            log.action(de.message)                       
    # dispatch command to add a normal graph node
    def dispatch_node(self, graph_id, node):                        
        if graph_id not in session.graphs:
            session.graphs[graph_id] = Graph()
            log.action("Initialized graph with id: '{}'".format(graph_id)) 
        # add node to session base graph
        session.graphs[graph_id].add_node(node)
        # update node in player copy
        try:
            session.players[graph_id].update_player_copy(node)
            log.action("Updating node: '{}' in player copy '{}'".format(node, graph_id))
        except KeyError as e:            
            log.action(" No player copy for graph: '{}', not updating!".format(graph_id))
        log.action("Adding node: '{}' to graph: '{}'".format(node, graph_id))
        # update eventual overlays
        self.update_lays(graph_id)
    def dispatch_edge(self, graph_id, edge, src):
        if graph_id not in session.graphs:
            raise DispatcherError("Graph '{}' not present, can't add edge!".format(graph_id))            
        graph = session.graphs[graph_id]
        if src not in graph.nodes or edge.dest not in graph.nodes:
            raise DispatcherError("Invalid edge, source or destination node not present!")        
        graph.add_edge(src, edge)
        try:
            session.players[graph_id].update_player_copy(edge)
            log.action("Updating edge: '{}' in player copy '{}'".format(edge, graph_id))
        except KeyError as e:            
            log.action(" No player copy for graph: '{}', not updating!".format(graph_id))
        log.action("Adding edge: '{}' to graph: '{}'".format(edge, graph_id))
        # update eventual overlays
        self.update_lays(graph_id)
    def dispatch_deletion(deletion):
        if deletion[1][0] is 'edge':
            
        elif if deletion[1][0] is 'node':

            
    def update_lays(self, graph_id):
        for player in session.players:
            if graph_id in session.players[player].overlays:
                session.players[player].update_overlay(graph_id)
            if graph_id in session.players[player].permalays:
                session.players[player].update_permalay(graph_id)
                
# class for dispatcher errors                
class DispatcherError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)
