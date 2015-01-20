#! /usr/bin/env python
import cmd, readline

from graa_scheduler import *
from graa_parser import *
from graa_dispatcher import *
from graa_base import *

# IDEAS:
# learning: store paths, rate performances, automatically play on that basis ? 
# centralized clock for collaborative graaing ?
# node locking mode ? (give nodes a duration ?)
# configurable resolution for non-realtime systems ? how, if it's strongly timed ... :(

# TO BE DONE:
# tbd: resetting graphs
# tbd: validation: all nodes reachable etc ?
# tbd: more fine-grained logging
# tbd: re-sync graphs on beat (restart command ?)
# tbd: graphs containing graphs, for longer compositions !
# tbd: edge probability modification 
# tbd: edge duration modification
# tbd: peristent modifications ?
# tbd: emacs mode
# tbd: disklavier backend
# tbd: supercollider backend
# tbd: multiple edges at once: b1-500->b2-500->b3 ?
# tbd: edge rebalancing (subtract equally from existing edges if not enough prob left)
# tbd: documentation
# tbd: play modes: markov, manual, beat (?)
# tbd: manual timeshift: d1@+/-x
# tbd: multi-command lines
# tbd: add overlay kwargs if not present
# tbd: mute nodes through overlays
# tbd: two overlay modes d+ol: non-persistent, only apply functions, d+=ol: store values
# tbd: note parser for midi backend
# tbd: write graph generators, like: tournament tr dirt~0:bd:0 5 1024 (tournament graph with 5 nodes...) (circle, bjoerklund)
# tbd: write graph transformers that workon the structure of the graph, like, reverse, tournament, rotate (?), revert, minspan, tsp
# tbd: load source files
# tbd: expand -> expandgraph to code in it's current state

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
        self.scheduler = GraaScheduler()
        self.beat = GraaBeat(self.session, self.scheduler)
        self.dispatcher = GraaDispatcher(self.session, self.beat)
        super().__init__()
    def do_hold(self, arg):
        'Hold graph in its current state.'
        self.dispatcher.dispatch([(GraaDispatcher.HOLD, arg)])
    def do_tempo(self, arg):
        'Set beat tempo (measured in BPM).'
        self.dispatcher.dispatch([(GraaDispatcher.TEMPO, arg)])
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
        for player_key in self.session.players:            
            player = self.session.players[player_key]
            if player.active:
                player.active = False
                player.graph_thread.join()
        print("Quitting, bye!")
        return True
    def do_expand(self, arg):
        print(self.session.graphs[arg])
    def do_play(self, arg):
        'Play graph. If graph already playing, don\'t.' 
        self.beat.collect_garbage_players(self.session)
        parsed_arg = self.parser.start_line.parseString(arg)
        self.dispatcher.dispatch([(GraaDispatcher.PLAY, parsed_arg)])
    def do_syntax(self, arg):
        """
 __,  ,_    __,   __,  
/  | /  |  /  |  /  |  
\_/|/   |_/\_/|_/\_/|_/
  /|                   
  \|        Version 0.1 
        
Syntax overview!
        
A node is specified as follows:

d1|dirt~0:casio:1

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
        keys = arg.split(":")
        self.dispatcher.dispatch([(GraaDispatcher.DELETE, keys)])                                           
    def default(self, arg):
        try:
            self.dispatcher.dispatch(self.parser.parse(arg))
        except ParseException:
            print("Invalid input! Please type \'help\' or \'?\' for assistance!")

# MAIN!!
if __name__ == '__main__':
    shell = GraaShell()
    shell.cmdloop()
    
