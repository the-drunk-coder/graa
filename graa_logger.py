"""
The logger class.

Handles the different log outputs.

"""

import sys
from graa_session import GraaSession as session

class GraaLogger():
    beat_outfile = open("beat_out", "a")
    action_outfile = open("action_out", "a")
    shell_outfile = sys.stdout
    def shell(msg):
        print(msg, file=GraaLogger.shell_outfile, flush=True)
    def beat(msg):
        print("@{}: ".format(session.now) + msg, file=GraaLogger.beat_outfile, flush=True)
    def action(msg):
        print("@{}: ".format(session.now) + msg, file=GraaLogger.action_outfile, flush=True)
