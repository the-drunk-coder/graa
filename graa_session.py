
"""
The Graa Session.

Contains all the graphs, overlays and some metadata in a session.

"""

class GraaSession():
    now = 0
    delay = 4
    graphs = {}
    players = {}
    # 117bpm results in 512ms per beat ... a nice, round number!
    tempo = 117
    # one beat as default
    default_duration = 512 
    active = False
    # the 'executors' to render the statements to time
    beat = None    
    scheduler = None
    dispatcher = None
