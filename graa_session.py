
"""
The Graa Session.

Contains all the graphs, overlays and some metadata in a session.

"""

class GraaSession():
    now = 0
    delay = 4
    graphs = {}
    players = {}
    overlays = {}
    # 117bpm results in 512ms per beat ... a nice, round number!
    tempo = 117
    active = False    
    beat = None    
    scheduler = None
    dispatcher = None
