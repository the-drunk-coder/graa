import random, math

def binomial(x, y):
    try:
        binom = math.factorial(x) // math.factorial(y) // math.factorial(x - y)
    except ValueError:
        binom = 0
    return binom

# some distribution functions ...
def poisson(val, func, inc, cyc, lamb):    
    "Function eval by poisson distribution over a certain cyclicity"
    #print(str(inc) + ":" + str(cyc))
    index = int(inc % cyc)
    prob = (pow(lamb, index) / math.factorial(index)) * math.exp(-lamb)
    random.seed()
    selecta = random.randint(0,99)
    if selecta < (prob * 100):
        return func
    else:
        return val

def hypergeo(val, func, inc, cyc, bigm, bign):
    "Function eval by hypergeometric distribution over a certain cyclicity"
    index = int(inc % cyc)
    prob = (binomial(bigm, index) * binomial(bign-bigm, cyc - index)) / binomial(bign, cyc)    
    selecta = random.randint(0,99)
    if selecta < (prob * 100):
        return func
    else:
        return val

def rndrange(a, b):
    return random.randrange(a,b)

def rndarg(*args):
    return random.choice(args)

def mod(i, j):
    return i % j

def add(i, j):    
    return i + j

def sub(i, j):
    return i - j  

def mul(i, j):
    return i * j  

def div(i, j):
    return i / j 

# value, incrementing param, steps for one cycle, range 
def sinstretch(val, inc, cyc, min_bound, max_bound):
    """
    Sinusoidal stretching of values between specified bounds
    """
    degree_increment = 360 / cyc
    degree = ((inc % cyc) * degree_increment) % 360
    abs_sin = abs(math.sin(math.radians(degree)))
    stretch_range = max_bound - min_bound
    ret = (abs_sin * stretch_range) + min_bound    
    return ret

    

def brownian(val, inc):
    #print("br VAL " + str(val) + " TYPE " + str(type(val)))
    #print("br INC " + str(inc) + " TYPE " + str(type(inc)))
    
    """
    Simplified Wiener Process.

    Only works as permalay.
    
    """
    random.seed()    
    val = val + random.choice([inc, -inc])
    #print("br RET " + str(val))
    return val


def tline(orig, goal, steps, curr_step):
    diff = goal - orig;
    if curr_step >= steps:
        return goal
    step_diff = steps - curr_step
    step_size = diff / steps
    #print(steps)
    #print(curr_step)
    #print(step_diff)
    #print(orig + (step_diff * step_size))
    return orig + (curr_step * step_size)
    

def bounds(val, bounda, boundb):
    #print("bounds")
    """
    Keep value between bounds.
    """
    max_bound = max(bounda, boundb)
    min_bound = min(bounda, boundb)
    if val <= min_bound:
        return min_bound
    elif val >= max_bound:
        return max_bound
    else:
        return val
    

def wrap(val, bounda, boundb):
    """
    Wrap value if it hits a bound.
    """
    max_bound = max(bounda, boundb)
    min_bound = min(bounda, boundb)    
    retval = None
    if val <= min_bound:        
        retval = max_bound
    elif val >= max_bound:        
        retval = min_bound        
    else:
        retval = val
        #print("BOUNDA    {} BOUNDB   {}   VAL {}     MIN {}     MAX {}    RET {}".format(bounda, boundb, val, min_bound, max_bound, retval))
    return retval
