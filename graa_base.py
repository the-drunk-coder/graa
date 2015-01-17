import threading, copy, random, _thread
from queue import Queue
from graa_structures import *
from graa_overlay_processors import * 

# default sound function library
import graa_sound_functions


"""
The Graa Session.

Contains all the graphs, overlays and some metadata in a session.

"""
class GraaSession():
    def __init__(self, outfile):
        self.graphs = {}
        self.players = {}
        self.overlays = {}
        # 117bpm results in 512ms per beat ... a nice, round number!
        self.tempo = 117
        self.active = True
        self.outfile = outfile


"""
The Graa Player.

Handles one graph and all its overlays.

Each graph lives in its own player, each player has its own thread.

"""
class GraaPlayer():   
    def __init__(self, session, graph_id, sched, delay=0):
        self.sched = sched
        self.session = session
        self.overlays = {}
        self.graph_id = graph_id
        self.graph_thread = threading.Thread(target=self.play, args=(session, graph_id))
        self.graph_thread.deamon = True
        self.active = False
        self.initial_delay = delay
    def start(self):
        self.active = True
        self.graph_thread.start()
    def hold(self):
        self.active = False
        self.graph_thread.join() 
    def add_overlay(self, overlay_id):
        # add a copy of the overlay, as each overlay should act independent for each player
        self.overlays[overlay_id] = copy.deepcopy(self.session.overlays[overlay_id])                                                      
    def update_overlay(self, overlay_id):
        current_overlay = self.overlays[overlay_id] 
        updated_overlay = copy.deepcopy(self.session.overlays[overlay_id])
        # update current node and step counter
        updated_overlay.current_node_id = current_overlay.current_node_id
        updated_overlay.nodes[updated_overlay.current_node_id].meta = current_overlay.nodes[current_overlay.current_node_id].meta
        self.overlays[overlay_id] = updated_overlay
    def play(self, session, graph_id):        
        if self.active:
            # process initial delay
            if self.initial_delay != 0:
                self.sched.time_function(self.play, [session, graph_id], {}, self.initial_delay)
                self.initial_delay = 0
            else:
                graph = session.graphs[graph_id]
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
                        print("Overlay {} on graph {} reached its end, removing!".format(ol_key, graph_id), file=session.outfile, flush=True)           
                        ol_to_remove.append(ol_key)
                    else:    
                        # append
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
                    self.sched_next_node(session, graph_id, graph.current_node_id)            
                except:                    
                    print("Couldn't schedule next node for graph {}, ending!".format(graph_id), file=session.outfile, flush=True)           
                    self.eval_node(session, current_node, current_overlay_dicts, current_overlay_steps)
                    return
                self.eval_node(session, current_node, current_overlay_dicts, current_overlay_steps)
    # TBD : apply edge mod, use step from node
    # schedule next node
    def sched_next_node(self, session, graph_id, current_node_id):
        chosen_edge = self.choose_edge(session, graph_id, current_node_id)
        #if there is no edgeleft, end this player!   
        edge = session.graphs[graph_id].edges[current_node_id][chosen_edge]
        session.graphs[graph_id].current_node_id = edge.dest        
        self.sched.time_function(self.play, [session, graph_id], {}, edge.dur)
    # choose edge for next transition
    def choose_edge(self, session, graph_id, node_id):        
        weights = [edge.prob for edge in session.graphs[graph_id].edges[node_id]]
        choice_list = []
        for i, weight in zip(range(len(weights)), weights):
           choice_list += [str(i)] * weight
        return int(random.choice(choice_list))
    # choose overlay edge
    def choose_overlay_edge(self, overlay_id, node_id):
        # end node 
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
            print("Couldn't evaluate a node. Please try again!", file=session.outfile, flush=True)           
            #raise


"""
The Graa Beat.

Takes care of starting and queuing graphs.

Not to be confused with the scheduler.

"""
class GraaBeat():
    def __init__(self, session, sched):
        self.sched = sched
        # LIFO Queue
        self.graph_queue = Queue()
        self.session = session
        self.beat_thread = threading.Thread(target=self.beat, args=(session,))
        self.beat_thread.deamon = True
        self.beat_thread.start()
    def queue_graph(self, graph_id):
        self.graph_queue.put(graph_id)
        print("Queuing graph with id: {}.".format(graph_id), file=self.session.outfile, flush=True)
    # function to be called by scheduler in separate process
    def beat(self, session):
        #print("beat, tempo: {}".format(session.tempo), file = session.outfile, flush=True)
        while not self.graph_queue.empty():
            graph_start = self.graph_queue.get()
            self.start_graph(session, graph_start[0], self.sched, graph_start[1])        
        # garbage collection
        delete_keys = []
        for player_key in self.session.players:
            if not self.session.players[player_key].graph_thread.is_alive():
                print("Putting player {} to garbage!".format(player_key), file=self.session.outfile, flush=True)
                delete_keys.append(player_key)
        while len(delete_keys) != 0:
            del self.session.players[delete_keys.pop()]
        if(session.active):
            #it's important only to use integers here !
            self.sched.time_function(self.beat, [session], {}, int((60.0 / session.tempo) * 1000))
    def start_graph(self, session, graph_id, sched, delay=0):
        # on-the-fly garbage collection
        if graph_id in session.players.keys() and not session.players[graph_id].graph_thread.is_alive():
            print("Putting player {} to garbage!".format(player_key), file=self.session.outfile, flush=True)
            del session.players[graph_id]
        if graph_id not in session.players:
            session.players[graph_id] = GraaPlayer(session, graph_id, sched, delay)            
        # this might happen if player was created by an overlay addition
        if session.players[graph_id].sched == None:
            session.players[graph_id].sched = sched
            session.players[graph_id].initial_delay = delay
        session.players[graph_id].start()
