import random

def randomvowel():
    return random.choice(['a', 'e', 'i', 'o', 'u'])

def add(i, j):
    return i + j  

def stepadd(i, j, step):
    return i + j + step

def stra(s, step):
    return s + ":" + str(step)
