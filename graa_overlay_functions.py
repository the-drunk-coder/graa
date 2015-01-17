import random

def rndvow():
    return random.choice(['a', 'e', 'i', 'o', 'u'])

def stepvow(step):
    vowels = ['a', 'e', 'i', 'o', 'u']
    return vowels[step % 5]

def mod(i, j):
    return int(i % j)

def add(i, j):
    return i + j  

def stepadd(i, j, step):
    return i + j + step

def stra(s, step):
    return s + ":" + str(step)
