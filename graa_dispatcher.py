from graa_structures import *
from graa_base import *
from graa_parser import *
from graa_logger import GraaLogger as log

"""
Dispatch parser output to session

"""
class GraaDispatcher():
    # dispatcher constants
    HOLD = "hold"
    TEMPO = "tempo"
    DELETE = "del"
    PLAY = "play"
    OVERLAY_EDGE = "ol_edge"
    NORMAL_EDGE = "n_edge"
    OVERLAY_NODE = "ol_node"
    NORMAL_NODE = "n_node"
    OL_APPLICATION = "ol_application"
    OL_REMOVAL = "ol_removal"
    def __init__(self, session, beat):
        self.session = session
        self.beat = beat
        self.scheduler = beat.sched
        self.dispatcher_map = {}
        self.dispatcher_map[GraaDispatcher.OVERLAY_NODE] = self.dispatch_overlay_node
        self.dispatcher_map[GraaDispatcher.OVERLAY_EDGE] = self.dispatch_overlay_edge
        self.dispatcher_map[GraaDispatcher.NORMAL_NODE] = self.dispatch_normal_node
        self.dispatcher_map[GraaDispatcher.NORMAL_EDGE] = self.dispatch_normal_edge
        self.dispatcher_map[GraaDispatcher.OL_APPLICATION] = self.dispatch_ol_application
        self.dispatcher_map[GraaDispatcher.OL_REMOVAL] = self.dispatch_ol_removal
        self.dispatcher_map[GraaDispatcher.HOLD] = self.hold
        self.dispatcher_map[GraaDispatcher.TEMPO] = self.tempo
        self.dispatcher_map[GraaDispatcher.DELETE] = self.delete_graph_or_overlay
        self.dispatcher_map[GraaDispatcher.PLAY] = self.play
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
        if ol_id in self.session.graphs:
            raise DispatcherError("Can't add overlay element to a graph!")            
        if ol_id not in self.session.overlays:
            self.session.overlays[ol_id] = Graph()
            log.action("Initialized overlay with id: {}".format(ol_id))            
        #initialize step counter with 0
        ol_node.meta = 0
        self.session.overlays[ol_id].add_node(ol_node)            
        # updating player copies of overlays
        for player_id in self.session.players:
            if ol_id in self.session.players[player_id].overlays:
                self.session.players[player_id].update_overlay(ol_id)
        log.action("Adding node: {} to overlay: {}'".format(ol_node, ol_id))
    def dispatch_overlay_edge(self, ol_id, ol_edge, src):
        if ol_id not in self.session.overlays:
            raise DispatcherError("Overlay {} not present, can't add edge!".format(ol_id))            
        overlay = self.session.overlays[ol_id]
        if src not in overlay.nodes or ol_edge.dest not in overlay.nodes:
            raise DispatcherError("Invalid overlay edge, source or destination node not present!")
        overlay.add_edge(src, ol_edge)
        # updating player copies of overlays
        for player_id in self.session.players:
            if ol_id in self.session.players[player_id].overlays:
                self.session.players[player_id].update_overlay(ol_id)                
        log.action("Adding edge: {} to overlay: {}'".format(ol_edge, ol_id))
    # dispatch command to add a normal graph node
    def dispatch_normal_node(self, graph_id, node):                
        if graph_id in self.session.overlays:
            raise DispatcherError("Can't add graph element to overlay!")            
        if graph_id not in self.session.graphs:
            self.session.graphs[graph_id] = Graph()
            log.action("Initialized graph with id: {}".format(graph_id)) 
        self.session.graphs[graph_id].add_node(node)
        log.action("Adding node: {} to graph: {}'".format(node, graph_id))
    def dispatch_normal_edge(self, graph_id, edge, src):
        if graph_id not in self.session.graphs:
            raise DispatcherError("Graph {} not present, can't add edge!".format(graph_id))            
        graph = self.session.graphs[graph_id]
        if src not in graph.nodes or edge.dest not in graph.nodes:
            raise DispatcherError("Invalid edge, source or destination node not present!")        
        graph.add_edge(src, edge)                                                  
        log.action("Adding edge: {} to graph: {}'".format(edge, graph_id))
    # dispatch the overlay application command        
    def dispatch_ol_application(self, graph_ids, overlay_ids):        
        for graph_id in graph_ids:            
            for overlay_id in overlay_ids:
                if graph_id == "all":                    
                    for key in self.session.graphs:                                
                        # if no player present for current graph, create one                        
                        if key not in self.session.players:                            
                            self.session.players[key] = GraaPlayer(self.session, key, None)
                        self.session.players[key].add_overlay(overlay_id)
                    log.action("Added overlay: {} to all graphs'".format(overlay_id))
                else:                    
                    # if no player present for current graph, create one                        
                    if graph_id not in self.session.players:                            
                        self.session.players[graph_id] = GraaPlayer(self.session, graph_id, None)
                    self.session.players[graph_id].add_overlay(overlay_id)
                    log.action("Added overlay: {} to graph: {}'".format(overlay_id, graph_id))
    def dispatch_ol_removal(self, graph_ids, overlay_ids):        
        for graph_id in graph_ids:            
            for overlay_id in overlay_ids:                
                if graph_id == "all":                    
                    for key in self.session.graphs:                                                                
                        try:
                            self.session.players[key].remove_overlay(overlay_id)
                        except:
                            log.action("Removing {} from {} failed, probably not added!".format(overlay_id, key))
                    log.action("Removed overlay: {} from all graphs'".format(overlay_id))
                else:
                    try:
                        self.session.players[graph_id].remove_overlay(overlay_id)
                    except:
                        log.action("Removing {} from {} failed, probably not added!".format(overlay_id, graph_id))
                    log.action("Removing overlay: {} from graph: {}'".format(overlay_id, graph_id))                    
    # hold a graph
    def hold(self, arg):
        if len(arg) == 0:
            log.action("Please specify graph!")
        else:
            try:
                if arg == "all":
                    for player_key in self.session.players:
                        self.session.players[player_key].hold()
                        self.session.players={}
                else:
                    for player_key in arg.split(":"):
                        self.session.players[player_key].hold()                   
                        del self.session.players[player_key]
            except:
                log.action("Couldn't hold graph, probably not played yet!")
    # change beat tempo
    def tempo(self, arg):
        try:
            self.session.tempo = int(arg)
            log.action("Beat tempo set to {} bpm!".format(self.session.tempo))
        except ValueError:
            log.action("Invalid tempo specification! - " + arg)
    def delete_graph_or_overlay(self, keys):
        for key in keys:
            # stop and remove player if playing
            if key in self.session.players:
                if self.session.players[key].active:
                    self.session.players[key].hold()               
                del self.session.players[key]
            # remove graph
            if key in self.session.graphs:
                del self.session.graphs[key]
            if key in self.session.overlays:
                for player in self.session.players.keys():
                    #remove overlay from players
                    if key in self.session.players[player].overlays:
                        del self.session.players[player].overlays[key]
                del self.session.overlays[key]
    def play(self, start_commands):
        for start_command in start_commands:
            if type(start_command) is str:
                if start_command not in self.session.graphs:
                    log.action("{} not found!".format(start_command))
                elif start_command in self.session.players and self.session.players[start_command].active:
                    log.action("{} already playing!".format(start_command))
                else:                                        
                    self.beat.queue_graph((start_command,0))
            else:
                gra_id = start_command[0]
                if gra_id not in self.session.graphs:
                    log.action("{} not found!".format(gra_id))
                # if graph has been initialized without starting
                elif gra_id not in self.session.players or not self.session.players[gra_id].active:
                    start_mode = start_command[1]
                    if start_mode == "now":
                        self.beat.start_graph(self.session, gra_id, self.scheduler)
                    elif type(start_mode) is int:
                        self.beat.queue_graph((gra_id, start_mode))
                else:
                    log.action("{} already playing!".format(gra_id))
                    
# class for dispatcher errors                
class DispatcherError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)
