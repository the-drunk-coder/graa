import threading, copy, random
from queue import Queue
from graa_structures import *
from graa_overlay_processors import * 
from graa_session import GraaSession as session
from graa_logger import GraaLogger as log

# default sound function library
import graa_sound_functions

"""
The Graa Player.

Handles one graph and all its overlays.

Each graph lives in its own player.

Each player con only be started once. That is, if you restart the graph,
a new player will be spawned

"""
class GraaPlayer():   
    def __init__(self, graph_id):        
        self.overlays = {}
        self.graph_id = graph_id        
        self.started = False
        self.active = False
        self.timestamp = 0
        self.delay = 0        
    def start(self):
        self.active = True
        self.started = True
        self.timestamp = session.now
        if(self.delay != 0):
            self.timestamp += self.delay
            session.scheduler.time_function(self.play, [], {}, self.timestamp)
            self.delay = 0
        else:
            self.play()
    def can_be_deleted(self):        
        # if a player has been started once, but is not active anymore, it can be deleted ...
        return not self.active and self.started
    # method only to be called from outside
    def hold(self):
        self.active = False
        self.graph_thread.join() 
    def add_overlay(self, overlay_id):
        # add a copy of the overlay, as each overlay should act independent for each player
        self.overlays[overlay_id] = copy.deepcopy(session.overlays[overlay_id])                                                      
    def remove_overlay(self, overlay_id):
        del self.overlays[overlay_id]
    def update_overlay(self, overlay_id):
        current_overlay = self.overlays[overlay_id] 
        updated_overlay = copy.deepcopy(self.session.overlays[overlay_id])
        # update current node and step counter
        updated_overlay.current_node_id = current_overlay.current_node_id
        updated_overlay.nodes[updated_overlay.current_node_id].meta = current_overlay.nodes[current_overlay.current_node_id].meta
        self.overlays[overlay_id] = updated_overlay
    def play(self, *args, **kwargs):        
        if self.active:                                     
            graph = session.graphs[self.graph_id]
            current_node = graph.nodes[graph.current_node_id]
            # collect overlay node functions in lists
            current_overlay_dicts = []
            current_overlay_steps = []
            # collect edge modificator functions in list
            dur_modificators = []
            prob_modificators = []
            ol_to_remove = []
            for ol_key in self.overlays:
                overlay = self.overlays[ol_key]
                current_overlay_dicts.append(overlay.nodes[overlay.current_node_id].content)
                current_overlay_steps.append(overlay.nodes[overlay.current_node_id].meta)
                ol_edge_id = self.choose_overlay_edge(ol_key, overlay.current_node_id)
                if ol_edge_id == None:
                    # overlay reached its end
                    log.action("Overlay {} on graph {} reached its end, removing!".format(ol_key, graph_id))           
                    ol_to_remove.append(ol_key)
                else:                            
                    ol_edge = overlay.edges[overlay.current_node_id][ol_edge_id]
                    if ol_edge.dur != None:
                        dur_modificators.append(ol_edge.dur)
                    if ol_edge.prob != None:
                        prob_modificators.append(ol_edge.prob)
                    # forward incrementation of step counter
                    overlay.nodes[ol_edge.dest].meta = overlay.nodes[overlay.current_node_id].meta + 1
                    overlay.current_node_id = ol_edge.dest
            while len(ol_to_remove) != 0:
                del self.overlays[ol_to_remove.pop()]
            try:
                self.sched_next_node(session, self.graph_id, graph.current_node_id)            
            except Exception as e:                    
                log.action("Couldn't schedule next node for graph {}, ending!".format(self.graph_id))           
                self.active = False
                self.eval_node(session, current_node, current_overlay_dicts, current_overlay_steps)
                return
            # otherwise, just eval 
            self.eval_node(session, current_node, current_overlay_dicts, current_overlay_steps)
    # TBD : apply edge mod, use step from node
    # schedule next node
    def sched_next_node(self, session, graph_id, current_node_id):
        chosen_edge = self.choose_edge(session, graph_id, current_node_id)
        #if there is no edgeleft, end this player!   
        edge = session.graphs[graph_id].edges[current_node_id][chosen_edge]
        session.graphs[graph_id].current_node_id = edge.dest
        self.timestamp += edge.dur + self.delay        
        session.scheduler.time_function(self.play, [], {}, self.timestamp)
        self.delay = 0
    # choose edge for next transition
    def choose_edge(self, session, graph_id, node_id):        
        random.seed()
        weights = [edge.prob for edge in session.graphs[graph_id].edges[node_id]]
        choice_list = []
        for i, weight in zip(range(len(weights)), weights):
           choice_list += [str(i)] * weight
        return int(random.choice(choice_list))
    # choose overlay edge
    def choose_overlay_edge(self, overlay_id, node_id):
        random.seed()
        if len(self.overlays[overlay_id].edges[node_id])== 0:
            return None
        weights = [edge.prob for edge in self.overlays[overlay_id].edges[node_id]]
        choice_list = []
        for i, weight in zip(range(len(weights)), weights):
           choice_list += [str(i)] * weight
        return int(random.choice(choice_list))
    # eval node content
    def eval_node(self, session, node, overlay_dicts, overlay_steps):
        try:
            args = node.content["args"]
            kwargs = node.content["kwargs"]
            for functions, step in zip(overlay_dicts, overlay_steps):
                args = replace_args(node.content["args"], functions, step)
                kwargs = replace_kwargs(node.content["kwargs"], functions, step)
            # try loading function from default library
            # evaluating the function string at runtime here, as
            # here might be a dynamic function library in the future ...                
            # print(args, file=session.outfile, flush=True)            
            getattr(graa_sound_functions, node.content["type"])(*args, **kwargs)            
        except:
            log.action("Couldn't evaluate a node. Please try again!")           
            raise


"""
The Graa Beat.

Takes care of starting and queuing graphs.

Not to be confused with the scheduler.

"""
class GraaBeat():
    def __init__(self):        
        # LIFO Queue
        self.graph_queue = Queue()
        # needed because of shitty scheduler
        # self.correction = 0
        self.starting_time = session.now
        self.timestamp = session.now
        self.beat()        
    def queue_graph(self, graph_id):
        self.graph_queue.put(graph_id)
        log.action("Queuing graph with id: {}.".format(graph_id))
    # garbage collection: delete deletable players
    def collect_garbage_players(self):
        deletable_players = [session.players[player_key].graph_id for player_key in session.players if session.players[player_key].can_be_deleted()]        
        if len(deletable_players) > 0:
            log.action("Putting players {} to garbage.".format(deletable_players))
        while len(deletable_players) != 0:            
            del session.players[deletable_players.pop()]
    # function to be called by scheduler in separate process    
    def beat(self, *args, **kwargs):        
        self.collect_garbage_players()
        # schedule next beat
        if(session.active):
            #it's important only to use integers here !
            self.timestamp += int((60.0 / session.tempo) * 1000)                       
            session.scheduler.time_function(self.beat, [], {}, self.timestamp)
            while not self.graph_queue.empty():
                graph_start = self.graph_queue.get()
                self.start_graph(graph_start)
    def start_graph(self, graph_id):
        if graph_id not in session.players:
            session.players[graph_id] = GraaPlayer(graph_id)            
        # this might happen if player was created by an overlay addition        
        session.players[graph_id].start()
