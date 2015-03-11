import copy, random
from queue import Queue
from graa_structures import *
from graa_session import GraaSession as session
from graa_logger import GraaLogger as log
from graa_function_evaluator import *

class GraaPlayer():
    """
    The Graa Player.

    Handles one graph and all its overlays.

    Each graph has a player copy, which lives in its own player.

    """
    def __init__(self, graph_id):
        # overlays and permalays for this graph
        self.overlays = {}
        self.permalays = {}
        # fetch player copy from graph store ...
        self.player_copy = copy.deepcopy(session.graphs[graph_id])
        self.graph_id = graph_id        
        self.started = False
        self.active = False
        self.paused = False
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
    def stop(self):
        self.active = False
    def pause(self):
        self.paused = True
    def resume(self):
        self.paused = False
        self.play()
    def add_overlay(self, overlay_id):
        # add a copy of the overlay, as each overlay should act independent for each player
        self.overlays[overlay_id] = copy.deepcopy(session.graphs[overlay_id])
    def add_permalay(self, permalay_id):
        # add a copy of the overlay, as each overlay should act independent for each player
        self.permalays[permalay_id] = copy.deepcopy(session.graphs[permalay_id])                                                      
    def remove_overlay(self, overlay_id):
        del self.overlays[overlay_id]
    def remove_permalay(self, permalay_id):
        del self.permalays[permalay_id]
    def update_overlay(self, overlay_id):
        current_overlay = self.overlays[overlay_id] 
        updated_overlay = copy.deepcopy(session.graphs[overlay_id])
        # update current node and step counter
        updated_overlay.current_node_id = current_overlay.current_node_id
        updated_overlay.nodes[updated_overlay.current_node_id].meta = current_overlay.nodes[current_overlay.current_node_id].meta
        self.overlays[overlay_id] = updated_overlay
    def update_permalay(self, permalay_id):
        current_permalay = self.permalays[permalay_id] 
        updated_permalay = copy.deepcopy(session.graphs[permalay_id])
        # update current node and step counter
        updated_permalay.current_node_id = current_permalay.current_node_id
        updated_permalay.nodes[updated_permalay.current_node_id].meta = current_permalay.nodes[current_permalay.current_node_id].meta
        self.permalays[permalay_id] = updated_permalay
    def update_player_copy(self, node_or_edge):        
        if type(node_or_edge) is Node:
            self.player_copy.add_node(node_or_edge)
        elif type(node_or_edge) is Edge:
            self.player_copy.add_edge(node_or_edge.source, node_or_edge)
    def play(self, *args, **kwargs):        
        if self.active and not self.paused:
            overlay_infos = self.collect_overlay_infos(self.overlays)
            permalay_infos = self.collect_overlay_infos(self.permalays)
            # remove finished over- and permalays
            while len(overlay_infos[3]) != 0:
                del self.overlays[overlay_infos[3].pop()]
            while len(permalay_infos[3]) != 0:
                del self.permalays[permalay_infos[3].pop()]
            current_node = self.player_copy.nodes[self.player_copy.current_node_id]
            # schedule the next node and end graph in case it's not possible
            try:
                self.sched_next_node(overlay_infos, permalay_infos)            
            except Exception as e:                    
                log.action("Couldn't schedule next node for graph {}, ending!".format(self.graph_id))           
                self.active = False
                self.eval_node(current_node, overlay_infos, permalay_infos)
                raise e
                return
            # otherwise, just eval the current node
            self.eval_node(current_node, overlay_infos, permalay_infos)
    # collect current nodes and edges from over- and permalays
    def collect_edge_mod_infos(self, lays):
        current_lay_dicts = []
        current_lay_steps = []
        dur_modificators = []
        prob_modificators = []
        lay_to_remove = []
        for lay_key in lays:
            lay = lays[lay_key]                
            step = lay.nodes[lay.current_node_id].meta
            # tuple format: (step, functions)
            current_lay_dicts.append((step, lay.nodes[lay.current_node_id].content))
            lay_edge_id = self.choose_edge(lay)
            if lay_edge_id == None:
                # overlay reached its end
                log.action("Overlay {} on graph {} reached its end, marked to remove!".format(ol_key, graph_id))           
                lay_to_remove.append(lay_key)
            else:                    
                lay_edge = lay.edges[lay.current_node_id][lay_edge_id]
                # remember: lay and dur are functions!
                if lay_edge.dur != None and lay_edge.dur != "nil":
                    dur_modificators.append((step, lay_edge.dur))
                if lay_edge.prob != None:
                    prob_modificators.append((step, lay_edge.prob))
                # forward incrementation of step counter
                lay.nodes[lay_edge.dest].meta = lay.nodes[lay.current_node_id].meta + 1
                lay.current_node_id = lay_edge.dest
        return (current_lay_dicts, dur_modificators, prob_modificators, lay_to_remove)
    def sched_next_node(self, overlay_infos, permalay_infos):
        #if there is no edge left, end this player!   
        edge = self.player_copy.edges[self.player_copy.current_node_id][self.choose_edge(self.player_copy)]
        self.player_copy.current_node_id = edge.dest
        # apply permanent duration mods
        current_dur = arg_eval(int, edge.dur, {})     
        for step, dur_mod in permalay_infos[1]:
            current_dur = func_eval(int, dur_mod, {"step": step, "dur":current_dur})
            edge.dur = current_dur
        # apply non-permanent duration mods
        for step, dur_mod in overlay_infos[1]:
            current_dur = func_eval(int, dur_mod, {"step": step, "dur":current_dur})
        # apply only permanent probability mods -- tbd later
        # current_prob = edge.prob
        # for prob_mod in permalay_infos[3]:
        #    current_prob = process_mod_function("prob", current_prob, 0, {"prob" : prob_mod})
        # edge.prob = current_prob
        # set next timestamp
        self.timestamp += current_dur + self.delay        
        session.scheduler.time_function(self.play, [], {}, self.timestamp)
        self.delay = 0
    # choose edge
    def choose_edge(self, graph):
        random.seed()
        if len(graph.edges[graph.current_node_id]) == 0:
            return None
        weights = [edge.prob for edge in graph.edges[graph.current_node_id]]
        choice_list = []
        for i, weight in zip(range(len(weights)), weights):
           choice_list += [str(i)] * weight
        return int(random.choice(choice_list))
    # eval node content
    def eval_node(self, node, overlay_infos, permalay_infos):
        try:
            # process permanant overlays            
            skip = False
            for step, functions in permalay_infos[0]:
                if type(functions) is str:
                    if functions == "nil":
                        continue
                    elif functions == "mute":
                        node.mute = True
                    elif functions == "unmute":
                        node.mute = False
                else:
                    #print("perma")
                    #print("PRE" + str(node.content))
                    process_arguments(node.content, functions, step)
            # process non-permanant overlays
            trans_func = copy.deepcopy(node.content)
            trans_mute = False
            for step, functions in overlay_infos[0]:
                if type(functions) is str:
                    if functions == "nil":
                        continue
                    elif functions == "mute":
                        trans_mute = True
                    elif functions == "unmute":
                        trans_mute = False
                else:
                    #print("over")
                    process_arguments(trans_func, functions, step)
            # evaluate transitory node function copy 
            if not (node.mute or trans_mute):
                func_eval(None, trans_func, {"$time":session.now})
        except:
            log.action("Couldn't evaluate a node. Please try again!")           
            raise


class GraaBeat():
    """
    The Graa Beat.

    Takes care of starting and queuing graphs.

    Not to be confused with the scheduler.

    """
    def __init__(self):        
        # LIFO Queue
        self.graph_queue = Queue()       
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
        if session.players[graph_id].paused:
            session.players[graph_id].resume()
        else:
            session.players[graph_id].start()
