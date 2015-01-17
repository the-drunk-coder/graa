#! /usr/bin/env python
import cmd, readline

from graa_scheduler import *
from graa_parser import *
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
# tbd: emacs mode
# tbd: disklavier backend
# tbd: supercollider backend
# tbd: multiple edges at once: b1-500->b2-500->b3 ?
# tbd: edge rebalancing (subtract equally from existing edges if not enough prob left)
# tbd: documentation
# tbd: play modes: markov, manual, beat (?)
# tbd: manual timeshift

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
                    for player_key in self.session.players:
                        self.session.players[player_key].hold()
                    self.session.players={}
                else:
                    for player_key in arg.split(":"):
                        self.session.players[player_key].hold()                   
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
        for player_key in self.session.players:            
            player = self.session.players[player_key]
            if player.active:
                player.active = False
                player.graph_thread.join()
        print("Quitting, bye!")
        return True
    def do_play(self, arg):
        'Play graph. Start on next beat. If graph already playing, don\'t.' 
        parsed_arg = self.parser.start_line.parseString(arg)
        for start_command in parsed_arg:
            if type(start_command) is str:
                if start_command not in self.session.graphs:
                    print("{} not found!".format(start_command))                    
                else:
                    # happens if oneshot graph has been played
                    if start_command in self.session.players and not self.session.players[start_command].graph_thread.is_alive():
                        print("Putting player {} to garbage!".format(start_command), file=self.session.outfile, flush=True)
                        del self.session.players[start_command]                
                    self.beat.queue_graph((start_command,0))
            else:
                gra_id = start_command[0]
                if gra_id not in self.session.graphs:
                    print("{} not found!".format(gra_id))
                # if graph has been initialized without startihg
                elif gra_id not in self.session.players or not self.session.players[gra_id].active:
                    start_mode = start_command[1]
                    if start_mode == "i":
                        self.beat.start_graph(self.session, gra_id, self.scheduler)
                    elif type(start_mode) is int:
                        self.beat.queue_graph((gra_id, start_mode))
                # if graph has been running once before
                elif gra_id in self.session.players and not self.session.players[gra_id].graph_thread.is_alive():
                    print("Putting player {} to garbage!".format(gra_id), file=self.session.outfile, flush=True)
                    del self.session.players[gra_id]                
                    start_mode = start_command[1]
                    if start_mode == "i":
                        self.beat.start_graph(self.session, gra_id, self.scheduler)
                    elif type(start_mode) is int:
                        self.beat.queue_graph((gra_id, start_mode))
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
                if self.session.players[key].active:
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
    
