import random, math

def rndvow():
    return random.choice(['a', 'e', 'i', 'o', 'u'])

def stepvow(step):
    vowels = ['a', 'e', 'i', 'o', 'u']
    return vowels[step % 5]

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

def stepadd(i, j, step):
    return i + j + step

def stra(s, step):
    return s + ":" + str(step)

# value, incrementing param, steps for one cycle, range 
def sinstretch(val, inc, cyc, min_bound, max_bound):
    degree_increment = 360 / cyc
    degree = ((inc % cyc) * degree_increment) % 360
    abs_sin = abs(math.sin(math.radians(degree)))
    stretch_range = max_bound - min_bound
    return (abs_sin * stretch_range) + min_bound 
    
