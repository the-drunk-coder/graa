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

def start_graa():
    """Initialize the graa> session."""    
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


def quit_graa():
    """Quit graa> and all it's functions."""
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
   

def stop(players):
    """
    Stop the specified graphs. Think of 'stop' as an your cd player.
    The graphs will be reset, overlays removed.

    Graphs should be specified in a string,
    as a comma-separated list of identifiers.
    """
    for key in players.split(","):
        if key == "all":
            for player_key in session.players:
                try:
                    session.players[player_key].stop()                    
                except Exception as e:
                    log.action("Couldn't hold graph, probably not played yet!")
                    raise e
            session.players={}
        else:
            try:
                session.players[key].stop()                   
                del session.players[key]
            except Exception as e:
                log.action("Couldn't hold graph '{}', probably not played yet!".format(key))
                raise e
# end stop()    


def pause(players):
    """
    Pause the specified graphs.
    Think of 'pause' as on your cd player. You can resume the graph in
    its current state.

    Graphs should be specified in a string,
    as a comma-separated list of identifiers.
    """
    for key in players.split(","):
        if key == "all":
            for player_key in session.players:
                try:
                    session.players[player_key].pause()
                except:
                    log.action("Couldn't pause graph, probably not played yet!")
        else:
            try:
                session.players[key].pause()                   
            except:
                log.action("Couldn't pause graph '{}', probably not played yet!".format(key))
# end pause()    



def tempo(arg):
    """Change tempo of underlying beat. Should adapt to your desired playing speed. """
    try:
        session.tempo = int(arg)
        log.action("Beat tempo set to {} bpm!".format(session.tempo))
    except ValueError:
        log.action("Invalid tempo specification! - " + arg)
# end tempo()


def delete(keys):
    """
    Delete specified graphs, with all consequences.
    Graphs should be specified in a string, as a comma-separated list of identifiers.

    Example:

    delete("a,b,c") - will delete graphs a, b and c
    
    """
    for key in keys.split(","):
        # stop and remove player if playing
        if key in session.players:
            if session.players[key].active:
                session.players[key].stop()               
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



def play(*args, **kwargs):
    """
    Play graphs. You may specify the graphs as one or more comma-separated list in one
    string, or multiple strings, or anything that returns a graph id ...

    You may specify an "imd" flag. If True, the graph will be started at once, if False (default),
    the graph will be started on next beats (faciliates synchronous start of multiple graphs).

    Example:
    
    play("a,b","c", d <<shift>> 256, imd=True) -- will immediately play graphs a,b,c, plus graph d with a timeshift.

    """
    session.beat.collect_garbage_players()
    for command in args:
        for key in command.split(","):
            key = key.strip()
            if key not in session.graphs:
                log.action("{} not found!".format(key))
            elif key in session.players and session.players[key].active and not session.players[key].paused:
                log.action("{} already playing!".format(key))
            else:
                immediately = kwargs.get("imd", False)
                if immediately:
                    session.beat.start_graph(key)
                else:
                    session.beat.queue_graph(key)
# end play()    

# shift a player by some milliseconds
@infix
def shift(graph_ids, delay):
    """
    Shift a graph by a specified amount of milliseconds. Use as infix:

    "graph_id" <<shift>> 256
    
    """
    for graph_id in graph_ids.split(","):
        if graph_id not in session.players:                            
            session.players[graph_id] = player(graph_id)
        session.players[graph_id].delay = delay
    return graph_ids
# end shift()

def expand(graph_id):
    """
    Expand a graph, that is, print its textual representation to the shell.

    You may specify a single graph.

    If the graph is playing, the player copy will be expanded, if not, the
    base graph will be used ...

    Mostly important for the emacs mode.
    
    """
    try:
        log.shell(session.players[graph_id].player_copy)
    except KeyError as e:
        log.shell(session.graphs[graph_id])        
# end expand()    


@infix
def plus(graph_ids, overlay_ids):
    """
    Add a non-destructive overlay graph to a graph. Use as infix.

    Example:

    "foo" <<plus>> "foo_ol" -- adds foo_ol to foo.
    
    """    
    for graph_id in graph_ids.split(","):
        if graph_id is "all":
            for key in session.graphs:
                for overlay_id in overlay_ids.split(","):
                    # if no player present for current graph, create one                        
                    if key not in session.players:                            
                        session.players[key] = player(key)
                    session.players[key].add_overlay(overlay_id)
            log.action("Added overlay: {} to all graphs'".format(overlay_id))
        else:
            for overlay_id in overlay_ids.split(","):
                # if no player present for current graph, create one                        
                if graph_id not in session.players:                            
                    session.players[graph_id] = player(graph_id)
                session.players[graph_id].add_overlay(overlay_id)
                log.action("Added overlay: {} to graph: {}'".format(overlay_id, graph_id))
    return graph_ids
# end plus()


@infix
def permaplus(graph_ids, permalay_ids):
    """
    Add a destructive overlay (permalay) graph to a graph. Use as infix.

    Example:

    "foo" <<plus>> "foo_ol" -- adds foo_ol to foo.
    
    """    
    for graph_id in graph_ids.split(","):
        if graph_id is "all":
            for key in session.graphs:
                for permalay_id in permalay_ids.split(","):
                    # if no player present for current graph, create one                        
                    if key not in session.players:                            
                        session.players[key] = player(key)
                    session.players[key].add_permalay(permalay_id)
            log.action("Added permalay: {} to all graphs'".format(permalay_id))
        else:
            for permalay_id in permalay_ids.split(","):
                # if no player present for current graph, create one                        
                if graph_id not in session.players:                            
                    session.players[graph_id] = player(graph_id)
                session.players[graph_id].add_permalay(permalay_id)
                log.action("Added permalay: {} to graph: {}'".format(permalay_id, graph_id))
    return graph_ids
# end permaplus


@infix
def minus(graph_ids, overlay_ids):
    """
    Remove an overlay graph from a graph. Use as infix.

    Example:

    "foo" <<minus>> "foo_ol" -- removes foo_ol from foo.
    
    """
    for graph_id in graph_ids.split(","):
        if graph_id is "all":
            for key in session.graphs:
                for overlay_id in overlay_ids.split(","):                    
                    session.players[key].remove_overlay(overlay_id)
                    session.players[key].remove_permalay(overlay_id)
            log.action("Remove over-/permalay: {} to all graphs'".format(overlay_id))
        else:
            for overlay_id in overlay_ids.split(","):
                session.players[graph_id].remove_overlay(overlay_id)
                log.action("Remove over-/permalay: {} to graph: {}'".format(overlay_id, graph_id))
    return graph_ids
# end minus()


def add(string):
    """
    Add graph data. The given data will be parsed and added as Nodes and Edges.

    Example:

    gaa1|dirt~1:casio:0,
    gaa1-500:100->gaa1
    
    This will add a graph with id 'gaa', containing one node and one edge.
    
    """
    for command in string.split(","):
        try:
            session.dispatcher.dispatch(parser.parse(command))
        except DispatcherError as de:
            log.action(de.message)
# end add()
        
