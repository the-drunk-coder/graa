#! /usr/bin/env python
import cmd, readline, time, sched, threading, random, imp
from pyparsing import *
from graa_structures import *
from queue import Queue
# default function library
import graa_fun

# ideas:
# node as function call, eval, node timing within node funciton
# don't modifiy the durations at player-level, but only in the data structure!

# improvements: use universal scheduler ?
# centralized clock for collaborative graaing ?

"""
The Player class.

Each graph lives in its own player, each player has its own thread.

"""
class GraaPlayer():   
    def __init__(self, session, graph_id):
        self.session = session
        self.graph_id = graph_id
        self.graph_thread = threading.Thread(target=self.start_play, args=(session, graph_id))
        self.graph_thread.deamon = True
        self.active = False
    def start(self):
        self.active = True
        self.graph_thread.start()
    def start_play(self, session, graph_id):
        self.sched = sched.scheduler(time.monotonic, time.sleep)
        self.play(session, graph_id)
        self.sched.run()
    def play(self, session, graph_id):
        graph = session.graphs[graph_id]
        current_node = graph.nodes[graph.current_node_id]
        self.eval_node(session, current_node)
        if(self.active):
            self.sched_next_node(session, graph_id, graph.current_node_id)
    # schedule next node
    def sched_next_node(self, session, graph_id, current_node_id):
        chosen_edge = self.choose_edge(session, graph_id, current_node_id)
        edge = session.graphs[graph_id].edges[current_node_id][chosen_edge]
        #print("chosen destinination: {}".format(edge.dest), file=session.outfile)
        session.graphs[graph_id].current_node_id = edge.dest
        if(self.active):
            self.sched.enter(edge.dur / 1000, 1, self.play, argument=(session, graph_id))        
    # choose edge for next transition
    def choose_edge(self, session, graph_id, node_id):
        weights = [edge.prob for edge in session.graphs[graph_id].edges[node_id]]
        choice_list = []
        for i, weight in zip(range(len(weights)), weights):
           choice_list += [str(i)] * weight
        return int(random.choice(choice_list))
    # eval node content
    def eval_node(self, session, node):
        # reload module, so you can toy around with it while playing
        try:
            imp.reload(GraaFun)
            getattr(GraaFun, node.content[0])(*node.content[1:])
        except:
            print("Couldn't evaluate node. Please try again!")
            raise
        
"""
The scheduler, taking care of the time and process spawning.

"""
class GraaScheduler():
    def __init__(self, session):
        self.graphs = {}
        # LIFO Queue
        self.graph_queue = Queue()
        self.session = session
        self.beat_thread = threading.Thread(target=self.start_beat, args=(session,))
        self.beat_thread.deamon = True
        self.beat_thread.start()
    #def start_graph(self, graph_id):
    def queue_graph(self, graph_id):
        self.graph_queue.put(graph_id)
        print("queuing graph with id: {}".format(graph_id))
    # function to be called by scheduler in separate process
    def start_beat(self, session):
        self.sched = sched.scheduler(time.monotonic, time.sleep)
        self.beat(session)
        self.sched.run() 
    def beat(self, session):
        #print("beat, tempo: {}".format(session.tempo), file = session.outfile, flush=True)
        while not self.graph_queue.empty():
            self.start_graph(session, self.graph_queue.get())
        if(session.active):
            self.sched.enter(60.0 / session.tempo, 1, self.beat, argument=(session,))
    def start_graph(self, session, graph_id):
        player = GraaPlayer(session, graph_id)
        session.players[graph_id] = player
        player.start()
        
        
"""
Contains all the graphs and some metadata in a session.

"""
class GraaSession():
    def __init__(self, outfile):
        self.graphs = {}
        self.players = {}
        self.tempo = 119
        self.active = True
        self.outfile = outfile
    def add_node(self, node_tuple):
        graph_id = node_tuple[0]
        if graph_id not in self.graphs:
            self.graphs[graph_id] = Graph()
            print("Initialized graph with id: \'" + graph_id + "\'")
        self.graphs[graph_id].add_node(node_tuple[1])
        print("Added node with id \'{}\' to graph \'{}\'".format(node_tuple[1].id, graph_id))
    def add_edge(self, edge_tuple):
        graph_id = edge_tuple[0]
        self.graphs[graph_id].add_edge(edge_tuple[1], edge_tuple[2])
        print("Added edge from node \'{}\' to node \'{}\' in graph {}!".format(edge_tuple[1],edge_tuple[2].dest, graph_id))
    
"""
Parse nodes and edges from the command line input 
 
"""
class GraaParser():
    #grammar rules for node and edge lines
    graph_id = Word(alphas)
    node_id = graph_id + Word(nums)
    node_type = Word(alphas)
    node_line = node_id + ":" + node_type + OneOrMore(":" + Word(alphanums))
    transition = Word(nums) + Optional(":" + Word(nums))
    edge_line = node_id + "-" + transition + "->" + node_id
    def parse_node(self, arg):
        node_list = self.node_line.parseString(arg, parseAll=True)
        graph_id = node_list[0]
        node_id = node_list[1]
        node_params = list(filter(lambda a: a != ":", node_list[2:]))
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
  \|

Welcome! Type \'help\' or \'?\' to list commands.\n
"""
    prompt = 'graa> '
    def __init__(self):
        outfile = open('out', 'a')
        self.session = GraaSession(outfile)
        self.parser = GraaParser()
        self.scheduler = GraaScheduler(self.session)
        super().__init__()
    def do_hold(self, arg):
        'Hold graph in its current state.'
        self.session.players[arg].active = False
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
        self.scheduler.beat_thread.join()
        for player_key in self.session.players.keys():
            player = self.session.players[player_key]
            player.active = False
            player.graph_thread.join()
        print("Quitting, bye!")
        return True
    def do_play(self, arg):
        'Play graph.'
        self.scheduler.queue_graph(arg)
    def do_syntax(self, arg):
        """
 __,  ,_    __,   __,  
/  | /  |  /  |  /  |  
\_/|/   |_/\_/|_/\_/|_/
  /|                   
  \|
        
Syntax overview!
        
A node is specified as follows:

<graph_id><node_id>:<node_type>:<param1>:...:<param_n>

An edge is specified as follows:

<graph_id><node_id_1>-<dur>:<prob>-><graph_id><node_id_2>

        """
    def default(self, arg):
        # ignore comment lines
        if arg[0] == "#":
            return False
        # this should be done better somehow
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
    
