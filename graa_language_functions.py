import sys, os
from infix import shift_infix as infix
from graa_session import GraaSession as session
from graa_logger import GraaLogger as log
from graa_base import GraaBeat as beat
from graa_base import GraaPlayer as player
from graa_scheduler import GraaScheduler as scheduler
from graa_dispatcher import GraaDispatcher as dispatcher
from graa_dispatcher import DispatcherError
from graa_parser import GraaParser as parser


# setup and start
def start_graa():
    session.active = True
    session.scheduler = scheduler()
    session.beat = beat()
    session.dispatcher = dispatcher()
    os.system('clear')
    sys.ps1 = "graa> "
    log.shell(
"""    
 __,  ,_    __,   __,  
/  | /  |  /  |  /  |  
\_/|/   |_/\_/|_/\_/|_/
  /|                   
  \|        Version 0.1

Welcome, dear follower of the cult of graa> !
""")    
# end start_graa()

# clean up and quit
def quit_graa():
    log.action("Quitting graa on next beat ... ")
    session.active = False
    session.scheduler.active = False
    session.scheduler.sched_thread.join()
    session.beat.beat_thread.join()
    for player_key in session.players:            
        player = session.players[player_key]
        if player.active:
            player.active = False
            player.graph_thread.join()
    log.action("Quitting, bye!")
    quit()
# end quit_graa()
   
# HOLD - hold a list of graphs
def hold(players):                   
    for key in players:
        if key == "all":
            for player_key in session.players:
                try:
                    session.players[player_key].hold()
                    session.players={}
                except:
                    log.action("Couldn't hold graph, probably not played yet!")
        else:
            try:
                session.players[key].hold()                   
                del session.players[key]
            except:
                log.action("Couldn't hold graph, probably not played yet!")
# end hold()    

# TEMPO - change beat tempo
def tempo(arg):
    try:
        session.tempo = int(arg)
        log.action("Beat tempo set to {} bpm!".format(session.tempo))
    except ValueError:
        log.action("Invalid tempo specification! - " + arg)
# end tempo()

# delete a list of graphs or overlays
def delete(keys):
    for key in keys:
        # stop and remove player if playing
        if key in session.players:
            if session.players[key].active:
                session.players[key].hold()               
            del session.players[key]
            # remove graph
        if key in session.graphs:
            del session.graphs[key]
        if key in session.overlays:
            for player in session.players.keys():
                #remove overlay from players
                if key in session.players[player].overlays:
                    del session.players[player].overlays[key]
                del session.overlays[key]
# end delete()

# command format: (graph_id, delay)
def play(*args, **kwargs):
    #session.beat.collect_garbage_players()
    for command in args:              
        if command[0] not in session.graphs:
            log.action("{} not found!".format(command[0]))
        elif command[0] in session.players and session.players[command[0]].active:
            log.action("{} already playing!".format(command[0]))
        else:
            if command[1] == "now":
                session.beat.start_graph(command[0])
            else:
                session.beat.queue_graph(command)
# end play()    

# shift a player by some milliseconds
@infix
def shift(graph_ids, delay):
    for graph_id in graph_ids.split(":"):
        if graph_id not in session.players:                            
            session.players[graph_id] = player(graph_id)
        session.players[graph_id].delay = delay
# end shift()

# expand a graph, that is, show all nodes and edges
def expand(graph_id):
    log.shell(session.graphs[graph_id])
# end expand()    

# add overlays
@infix
def plus(graph_ids, overlay_ids):        
    if type(graph_ids) is str and graph_ids == "all":                    
        for key in session.graphs:
            for overlay_id in overlay_ids:
                # if no player present for current graph, create one                        
                if key not in session.players:                            
                    session.players[key] = player(key)
                session.players[key].add_overlay(overlay_id)
                log.action("Added overlay: {} to all graphs'".format(overlay_id))
    elif type(graph_ids) is list:
        for graph_id in graph_ids:
            for overlay_id in overlay_ids:
                # if no player present for current graph, create one                        
                if graph_id not in session.players:                            
                    session.players[graph_id] = player(graph_id)
                session.players[graph_id].add_overlay(overlay_id)
                log.action("Added overlay: {} to graph: {}'".format(overlay_id, graph_id))
# end plus_ol()

# remove overlays
@infix
def minus(self, graph_ids, overlay_ids):        
    if type(graph_ids) is str and graph_ids == "all":                    
        for key in session.graphs:
            for overlay_id in overlay_ids:                
                try:
                    session.players[key].remove_overlay(overlay_id)
                except:
                    log.action("Removing {} from {} failed, probably not added!".format(overlay_id, key))
                log.action("Removed overlay: {} from all graphs'".format(overlay_id))
    elif type(graph_ids) is list:
        for graph_id in graph_ids:            
            for overlay_id in overlay_ids:               
                try:
                    session.players[graph_id].remove_overlay(overlay_id)
                except:
                    log.action("Removing {} from {} failed, probably not added!".format(overlay_id, graph_id))
                log.action("Removing overlay: {} from graph: {}'".format(overlay_id, graph_id))                    
# end minus_ol()

# add graph data
def add(string):
    for command in string.split(","):
        try:
            session.dispatcher.dispatch(parser.parse(command))
        except DispatcherError as de:
            log.action(de.message)
# end add()
        
