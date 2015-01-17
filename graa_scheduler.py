import threading
from pygame import time

outfile = open("out", "a")

"""

A somewhat naive function scheduler ...

"""
class GraaScheduler():
    def __init__(self):
        self.active = False
        self.schedict = {}
        self.stack = []
        self.sched_thread = threading.Thread(target=self.start, args=(self.schedict,self.stack))
        self.sched_thread.start()
    def start(self, schedict, stack):
        self.active = True
        self.sched_loop(schedict, stack)
    def sched_loop(self, schedict, stack):
        while self.active:
            now = time.get_ticks() - 1
            past = now
            correction = 0
            # check last few slots in case the wait wasn't precise
            while past > now - 5:
                if past in schedict:
                    for func_tuple in schedict[past]:
                        #print("playing function at: {}".format(past))
                        try:
                            func_tuple[0](*func_tuple[1],**func_tuple[2])
                        except:
                            print("Couldn't execute scheduled function!", file=outfile, flush=True)
                            raise
                    del schedict[past]
                    correction = now - past
                    break
                past = past - 1
            # now schedule pending events ... thus we're having a fixed point of time ('now')
            while len(stack) > 0:
                delayed_event = stack.pop()
                # correct future time if wait was not precise
                future_time = now - correction + delayed_event[0]
                print("now: {} delay: {} for: {} correction: {}".format(now, delayed_event[0], future_time, correction), file = outfile, flush = True)
                #print("correction: {}".format(correction))
                if future_time not in self.schedict:
                    self.schedict[future_time] = []    
                self.schedict[future_time].append((delayed_event[1], delayed_event[2], delayed_event[3]))
            # wait one microsecond 
            time.wait(1)
    # schedule a function to a later point of time 
    def time_function(self, func, args, kwargs, delay):
        self.stack.append([delay, func, args, kwargs])
        
    
