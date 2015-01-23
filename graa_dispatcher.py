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
       self.dispatcher_map[parser.OVERLAY_NODE] = self.dispatch_overlay_node
       self.dispatcher_map[parser.OVERLAY_EDGE] = self.dispatch_overlay_edge
       self.dispatcher_map[parser.NORMAL_NODE] = self.dispatch_normal_node
       self.dispatcher_map[parser.NORMAL_EDGE] = self.dispatch_normal_edge        
    # The main dispatcher function, bridge between parser and code execution
    def dispatch(self, parser_output):
        elem = parser_output[0]
        try:
            self.dispatcher_map[elem[0]](*elem[1:])
        except KeyError:
            log.action("Can't dispatch {}, no dispatcher present!".format(elem))
        except DispatcherError as de:
            log.action(de.message)            
    # dispatch overlay output from parser
    def dispatch_overlay_node(self, ol_id, ol_node):
        if ol_id in session.graphs:
            raise DispatcherError("Can't add overlay element to a graph!")            
        if ol_id not in session.overlays:
            session.overlays[ol_id] = Graph()
            log.action("Initialized overlay with id: {}".format(ol_id))            
        #initialize step counter with 0
        ol_node.meta = 0
        log.action("Adding node: {} to overlay: {}'".format(ol_node, ol_id))
    def dispatch_overlay_edge(self, ol_id, ol_edge, src):
        if ol_id not in session.overlays:
            raise DispatcherError("Overlay {} not present, can't add edge!".format(ol_id))            
        overlay = session.overlays[ol_id]
        if src not in overlay.nodes or ol_edge.dest not in overlay.nodes:
            raise DispatcherError("Invalid overlay edge, source or destination node not present!")
        overlay.add_edge(src, ol_edge)
        # updating player copies of overlays
        for player_id in session.players:
            if ol_id in session.players[player_id].overlays:
                session.players[player_id].update_overlay(ol_id)                
        log.action("Adding edge: {} to overlay: {}'".format(ol_edge, ol_id))
    # dispatch command to add a normal graph node
    def dispatch_normal_node(self, graph_id, node):                
        if graph_id in session.overlays:
            raise DispatcherError("Can't add graph element to overlay!")            
        if graph_id not in session.graphs:
            session.graphs[graph_id] = Graph()
            log.action("Initialized graph with id: {}".format(graph_id)) 
        session.graphs[graph_id].add_node(node)
        log.action("Adding node: {} to graph: {}'".format(node, graph_id))
    def dispatch_normal_edge(self, graph_id, edge, src):
        if graph_id not in session.graphs:
            raise DispatcherError("Graph {} not present, can't add edge!".format(graph_id))            
        graph = session.graphs[graph_id]
        if src not in graph.nodes or edge.dest not in graph.nodes:
            raise DispatcherError("Invalid edge, source or destination node not present!")        
        graph.add_edge(src, edge)                                                  
        log.action("Adding edge: {} to graph: {}'".format(edge, graph_id))
        
# class for dispatcher errors                
class DispatcherError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)
