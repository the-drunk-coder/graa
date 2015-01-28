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
        #last_now = 0
        while self.active:
            now = time.get_ticks() - 1
            session.now = now                               
            # now schedule pending events ... thus we're having a fixed point of time ('now')
            while len(stack) > 0:
                delayed_event = stack.pop()
                # correct future time if wait was not precise
                future_time = delayed_event[0]               
                log.beat("Add {} for timestamp: {}".format(delayed_event[1], future_time))
                if future_time not in self.schedict:
                    self.schedict[future_time] = []    
                self.schedict[future_time].append((delayed_event[1], delayed_event[2], delayed_event[3]))
            #after everything has been said and done, check if there's any garbage left ...
            time_keys = self.schedict.keys()
            pasts = [x for x in time_keys if x < now]
            for past in pasts:                    
                for func_tuple in schedict[past]:
                    #print("playing function at: {}".format(past))
                    try:
                        log.beat("Exec {}, orig {}, error {}".format(func_tuple[0], past, now - past))
                        async = threading.Thread(target=func_tuple[0], args=(func_tuple[1],func_tuple[2]))
                        async.start()
                    except Exception as e:
                        print(e)
                        log.beat("Couldn't execute scheduled function!")
                        # don't raise, as failed function execution shouldn't break the performance
                        raise e
                del schedict[past]
            #log.leap(last_now, now, now - last_now)
            #last_now = now
            # wait one microsecond              
            time.wait(1) 
    # schedule a function to a later point of time 
    def time_function(self, func, args, kwargs, timestamp):        
        self.stack.append([timestamp, func, args, kwargs])
        
    
