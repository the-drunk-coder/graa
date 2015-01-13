#! /usr/bin/env python
import cmd, readline, time, sched, threading, random, imp, copy
from pyparsing import *
from graa_structures import *
from graa_scheduler import *
from queue import Queue
# default function library
import graa_fun
import graa_mod

# IDEAS:
# don't modifiy the durations at player-level, but only in the data structure!
# learning: store paths, rate performances, automatically play on that basis ? 
# centralized clock for collaborative graaing ?
# node locking mode ? (give nodes a duration ?)
# configurable resolution for non-realtime systems ? how, if it's strongly timed ... :(

# TO BE DONE:
# tbd MULTIPLE COMMANDS! (emacs mode?)
# tbd: removing graphs
# tbd: resetting graphs
# tbd: validation: all nodes reachable etc ?
# tbd: more fine-grained logging
# tbd: overlay graphs
# tbd: handle end nodes
# re-sync graphs on beat (restart command ?)
# graphs containing graphs, for longer compositions !
# GENERATOR OVERLAYS !!!!!

# Overlay Syntax:
# ol1:<func>:<params> (omit params if only duration should be modified)
# ol1-<duration_mod_function>-<prob>->ol1 (duration mod function can be ommitted if duration should not be modified, as can the prob if there's
# only one edge ... otherwise the same rules apply)
# ol <ol_id> define overlay
# ol a <ol_od>:<graphs>
# ol d <ol_id>:<graphs>
# ol del <ol_id> delete overlay

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
    def play(self, session, graph_id):
        graph = session.graphs[graph_id]
        current_node = graph.nodes[graph.current_node_id]
        if(self.active):
            self.sched_next_node(session, graph_id, graph.current_node_id)
            self.eval_node(session, current_node)
    # schedule next node
    def sched_next_node(self, session, graph_id, current_node_id):
        chosen_edge = self.choose_edge(session, graph_id, current_node_id)
        
        edge = session.graphs[graph_id].edges[current_node_id][chosen_edge]
        # INSERT HERE: overlay edge modification application 
        # print("chosen destinination: {}".format(edge.dest), file=session.outfile, flush=True)
        
        session.graphs[graph_id].current_node_id = edge.dest
        self.sched.time_function(self.play, [session, graph_id], {}, edge.dur)        
    # choose edge for next transition
    def choose_edge(self, session, graph_id, node_id):
        weights = [edge.prob for edge in session.graphs[graph_id].edges[node_id]]
        choice_list = []
        for i, weight in zip(range(len(weights)), weights):
           choice_list += [str(i)] * weight
        return int(random.choice(choice_list))
    # eval node content
    def eval_node(self, session, node):
        #print("EVAL!!")
        try:
            #filter out args and kwargs
            args = []
            kwargs = {}
            for arg in node.content[1:]:
                # devide named and unnamed arguments
                if "=" in arg:
                    kvpair = arg.split("=")
                    kwargs[kvpair[0]] = kvpair[1]
                else:
                    args.append(arg)
            # try loading function from default library
            getattr(graa_fun, node.content[0])(*args, **kwargs)
            # print(str(node.content), file=session.outfile, flush=True)
        except:
            print("Couldn't evaluate a node. Please try again!", file=session.outfile, flush=True)
            #raise
        
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
    def add_node(self, node_tuple):
        graph_id = node_tuple[0]
        if graph_id not in self.graphs:
            self.graphs[graph_id] = Graph()
            print("Initialized graph with id: \'" + graph_id + "\'", file=self.outfile, flush=True)
        self.graphs[graph_id].add_node(node_tuple[1])
        print("Added node with id \'{}\' to graph \'{}\'".format(node_tuple[1].id, graph_id), file=self.outfile, flush=True)
    def add_edge(self, edge_tuple):
        graph_id = edge_tuple[0]
        self.graphs[graph_id].add_edge(edge_tuple[1], edge_tuple[2])
        print("Added edge from node \'{}\' to node \'{}\' in graph {}!".format(edge_tuple[1],edge_tuple[2].dest, graph_id), file=self.outfile, flush=True)
    
"""
Parse nodes and edges from the command line input 
 
"""
class GraaParser():
    #grammar rules for node and edge lines
    graph_id = Word(alphas)
    node_id = graph_id + Word(nums)
    node_type = Word(alphas)
    node_param = Word(alphanums) ^ Word(alphanums + "=" + alphanums) ^ Word(alphanums + "=" + nums + "." + nums )                      
    node_line = node_id + "|" + node_type + OneOrMore(":" + node_param)
    transition = Word(nums) + Optional(":" + Word(nums))
    edge_line = node_id + "-" + transition + "->" + node_id
    def parse_node(self, arg):
        node_list = self.node_line.parseString(arg, parseAll=True)
        graph_id = node_list[0]
        node_id = node_list[1]
        node_params = list(filter(lambda a: a not in [":", "|"], node_list[2:]))
        print(node_params)
        # create and return node
        return (graph_id, Node(node_id, node_params))
    def parse_edge(self, arg):
        edge_list = self.edge_line.parseString(arg, parseAll=True)
        graph_id = edge_list[0]
        source_node_id = edge_list[1]
        destination_node_id = edge_list[-1]
        duration = int(edge_list[3])
        edge = Edge(destination_node_id, duration)
        if edge_list[4] == ":":
            edge.prob = int(edge_list[5])
        return (graph_id, source_node_id, edge)
   
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
        self.parser = GraaParser()
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
        'Print specified digraph to file.'
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
        'Play graph. Start on next beat. If graph already playing, don\'t.'
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

<graph_id><node_id>:<node_type>:<param1>:...:<param_n>

An edge is specified as follows:

<graph_id><node_id_1>-<dur>:<prob>-><graph_id><node_id_2>

        """
        print("Dummy command for syntax help!")
    def default(self, arg):
        # ignore comment lines
        if arg[0] == "#":
            return False
        # this should probably be done better somehow, but it works out for now
        try:
            self.session.add_node(self.parser.parse_node(arg))
            # print(node_results)
        except ParseException:
            #print(str(Error))
            try:
                self.session.add_edge(self.parser.parse_edge(arg))
                # print(edge_results)
            except ParseException:
                print("Invalid input! Please type \'help\' or \'?\' for assistance!")
            except KeyboardInterrupt:
                return self.do_quit()
            except:
                raise
   
if __name__ == '__main__':
    shell = GraaShell()
    shell.cmdloop()
    
