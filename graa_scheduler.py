import threading
from pygame import time
from graa_session import GraaSession as session
from graa_logger import GraaLogger as log


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
            session.now = now
            past = now
            correction = 0
            # check last few slots in case the wait wasn't precise
            while past > now - 5:
                if past in schedict:
                    for func_tuple in schedict[past]:
                        #print("playing function at: {}".format(past))
                        try:
                            async = threading.Thread(target=func_tuple[0], args=(func_tuple[1],func_tuple[2]))
                            async.start()
                        except:
                            log.beat("Couldn't execute scheduled function!")
                            # don't raise, as failed function execution shouldn't break the performance
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
                log.beat("delay: {} for: {} correction: {}".format(delayed_event[0], future_time, correction))
                if future_time not in self.schedict:
                    self.schedict[future_time] = []    
                self.schedict[future_time].append((delayed_event[1], delayed_event[2], delayed_event[3]))
            # wait one microsecond 
            time.wait(1)
    # schedule a function to a later point of time 
    def time_function(self, func, args, kwargs, delay):
        self.stack.append([delay, func, args, kwargs])
        
    
