#! /usr/bin/env python
import cmd, readline, time, sched, threading, random, imp, copy
from queue import Queue
from graa_structures import *
from graa_parser import *
from graa_scheduler import *
from graa_overlay_processors import * 

# default sound function library
import graa_sound_functions

# IDEAS:
# learning: store paths, rate performances, automatically play on that basis ? 
# centralized clock for collaborative graaing ?
# node locking mode ? (give nodes a duration ?)
# configurable resolution for non-realtime systems ? how, if it's strongly timed ... :(

# TO BE DONE:
# tbd: resetting graphs
# tbd: validation: all nodes reachable etc ?
# tbd: more fine-grained logging
# tbd: handle end nodes
# tbd: re-sync graphs on beat (restart command ?)
# tbd: graphs containing graphs, for longer compositions !
# tbd: edge probability modification
# tbd: emacs mode
# tbd: play delay
# tbd: disklavier backend
# tbd: supercollider backend
# tbd: multiple edges at once: b1-500->b2-500->b3 ?
# tbd: edge rebalancing (subtract equally from existing edges if not enough prob left)
# tbd: update overlays in playing graphs 
# tbd: documentation

"""
The Player class.

Each graph lives in its own player, each player has its own thread.

"""
class GraaPlayer():   
    def __init__(self, session, graph_id, sched):
        self.sched = sched
        self.session = session
        self.overlays = {}
        self.graph_id = graph_id
        self.graph_thread = threading.Thread(target=self.play, args=(session, graph_id))
        self.graph_thread.deamon = True
        self.active = False
    def start(self):
        self.active = True
        self.graph_thread.start()
    def add_overlay(self, overlay_id):
        # add a copy of the overlay, as each overlay should act independent for each player
        self.overlays[overlay_id] = copy.deepcopy(self.session.overlays[overlay_id])                                                  
    def remove_overlay(self, overlay_id):        
        del self.overlays[overlay_id]
    def play(self, session, graph_id):
        graph = session.graphs[graph_id]
        current_node = graph.nodes[graph.current_node_id]
        # collect overlay node functions in lists
        current_overlay_dicts = []
        current_overlay_steps = []
        # collect edge modificator functions in list
        dur_modificators = []
        prob_modificators = []
        for ol_key in self.overlays.keys():
            overlay = self.overlays[ol_key]
            current_overlay_dicts.append(overlay.nodes[overlay.current_node_id].content)
            current_overlay_steps.append(overlay.nodes[overlay.current_node_id].meta)
            ol_edge_id = self.choose_overlay_edge(ol_key, overlay.current_node_id)
            # append
            ol_edge = overlay.edges[overlay.current_node_id][ol_edge_id]
            if ol_edge.dur != None:
                dur_modificators.append(ol_edge.dur)
            if ol_edge.prob != None:
                prob_modificators.append(ol_edge.prob)
            # forward incrementation of step counter
            overlay.nodes[ol_edge.dest].meta = overlay.nodes[overlay.current_node_id].meta + 1
            overlay.current_node_id = ol_edge.dest
        if(self.active):
            self.sched_next_node(session, graph_id, graph.current_node_id)
            self.eval_node(session, current_node, current_overlay_dicts, current_overlay_steps)
    # TBD : apply edge mod, use step from node
    # schedule next node
    def sched_next_node(self, session, graph_id, current_node_id):
        chosen_edge = self.choose_edge(session, graph_id, current_node_id)
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
            print(args, file=session.outfile, flush=True)
            getattr(graa_sound_functions, node.content["type"])(*args, **kwargs)            
        except:
            print("Couldn't evaluate a node. Please try again!", file=session.outfile, flush=True)           
            raise


                
"""
The beat, taking care of starting graphs etc
(might find a better naming, this was the sceduler originally ...)

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
        print("queuing graph with id: {}".format(graph_id), file=self.session.outfile, flush=True)
    # function to be called by scheduler in separate process
    def beat(self, session):
        #print("beat, tempo: {}".format(session.tempo), file = session.outfile, flush=True)
        while not self.graph_queue.empty():
            self.start_graph(session, self.graph_queue.get(), self.sched)
        if(session.active):
            #it's important only to use integers here !
            self.sched.time_function(self.beat, [session], {}, int((60.0 / session.tempo) * 1000))
    def start_graph(self, session, graph_id, sched):
        player = GraaPlayer(session, graph_id, sched)
        session.players[graph_id] = player
        player.start()
        
"""
Contains all the graphs and some metadata in a session.

"""
class GraaSession():
    def __init__(self, outfile):
        self.graphs = {}
        self.players = {}
        self.overlays = {}
        self.tempo = 120
        self.active = True
        self.outfile = outfile
       
"""
The main shell

"""
class GraaShell(cmd.Cmd):
    intro = """    
 __,  ,_    __,   __,  
/  | /  |  /  |  /  |  
\_/|/   |_/\_/|_/\_/|_/
  /|                   
  \|        Version 0.1

Welcome! Type \'help\' or \'?\' to list commands.\n
"""
    prompt = 'graa> '
    def __init__(self):
        outfile = open('out', 'a')
        self.session = GraaSession(outfile)
        self.parser = GraaParser
        self.dispatcher = GraaDispatcher(self.session)
        self.scheduler = GraaScheduler()
        self.beat = GraaBeat(self.session, self.scheduler)
        super().__init__()
    def do_hold(self, arg):
        'Hold graph in its current state.'
        if len(arg) == 0:
            print("Please specify graph!")
        else:
            try:
                if arg == "all":
                    for player_key in self.session.players.keys():
                        self.session.players[player_key].active = False
                        self.session.players[player_key].graph_thread.join()
                    self.session.players={}
                else:
                    for player_key in arg.split(":"):
                        self.session.players[player_key].active = False
                        self.session.players[player_key].graph_thread.join()
                        del self.session.players[player_key]
            except:
                print("Couldn't hold graph, probably not played yet!")
    def do_tempo(self, arg):
        'Set beat tempo (measured in BPM).'
        try:
            self.session.tempo = int(arg)
            print("Beat tempo set to {} bpm!".format(self.session.tempo))
        except ValueError:
            print("Invalid tempo specification! - " + arg)
    def do_print(self, arg):
        'Print specified graaph to file.'
        self.session.graphs[arg].render("graph_" + arg, "comment")
        print('tbd')
    def do_quit(self, arg):
        'Quit graa.'
        print("Quitting graa on next beat ... ")
        self.session.active = False
        self.scheduler.active = False
        self.scheduler.sched_thread.join()
        self.beat.beat_thread.join()
        for player_key in self.session.players.keys():
            player = self.session.players[player_key]
            player.active = False
            player.graph_thread.join()
        print("Quitting, bye!")
        return True
    def do_play(self, arg):
        'Play graaph. Start on next beat. If graph already playing, don\'t.'
        # tbd: check if graph is already playing, to avoid collisions
        for gra_id in arg.split(":"):            # check if graph is already playing ...
            if gra_id not in self.session.graphs.keys():
                print("{} not found!".format(gra_id))
            elif gra_id not in self.session.players.keys():
                self.beat.queue_graph(gra_id)
            else:
                print("{} already playing!".format(gra_id))
    def do_iplay(self, arg):
        'Play graph. Start immediately. If graph is already playing, don\'t.'
        for gra_id in arg.split(":"):
            # check if graph is already playing ...
            if gra_id not in self.session.players.keys():
                self.beat.start_graph(self.session, gra_id)
            else:
                print("{} already playing!".format(gra_id))
    def do_syntax(self, arg):
        """
 __,  ,_    __,   __,  
/  | /  |  /  |  /  |  
\_/|/   |_/\_/|_/\_/|_/
  /|                   
  \|        Version 0.1 
        
Syntax overview!
        
A node is specified as follows:

d1|dirt:0:casio:1

This will specify a graph called 'd' and a
node with id '1', using dirt as backend
        
An edge is specified as follows:

d1-500:100->d1

This will specify an edge from d1 to itself,
with a duration of 500ms and a probability of 100%!

        """
        print("Dummy command for syntax help!")
    def do_del(self, arg):
        "Delete graph or overlay, with all consequences!"
        for key in arg.split(":"):
            # stop and remove player if playing
            if key in self.session.players:
                self.session.players[key].active = False
                self.session.players[key].graph_thread.join()
                del self.session.players[key]
            # remove graaph
            if key in self.session.graphs:
                del self.session.graphs[key]
            if key in self.session.overlays:
                for player in self.session.players.keys():
                    #remove overlay from players
                    if key in self.session.players[player].overlays:
                        del self.session.players[player].overlays[key]
                del self.session.overlays[key]                               
    def default(self, arg):
        try:
            self.dispatcher.dispatch(self.parser.parse(arg))
        except ParseException:
            print("Invalid input! Please type \'help\' or \'?\' for assistance!")
        except DispatcherError as de:
            print(de.message)

        

# MAIN!!
if __name__ == '__main__':
    shell = GraaShell()
    shell.cmdloop()
    
