#!/usr/bin/env python

import math
import random
from itertools import *

# argmax from
# http://stackoverflow.com/questions/5098580/implementing-argmax-in-python

# given an iterable of pairs return the key corresponding to the greatest value
def argmax(pairs):
    return max(pairs, key=lambda a_b: a_b[1])[0]

# given an iterable of values return the index of the greatest value
def argmax_index(values):
    return argmax(zip(count(), values))

# given an iterable of keys and a function f, return the key with largest f(*key)
def argmax_f(keys, func):
    return max(map(lambda key: (func(*key), key), keys))[1]


def shuffled(l):
    x = l[:]
    random.shuffle(x)
    return x


def mean(lst):
    """Throws a div by zero exception if list is empty"""
    return sum(lst) / float(len(lst))

def stddev(lst):
    if len(lst) == 0:
        return 0
    m = mean(lst)
    return math.sqrt(sum((x-m)*(x-m) for x in lst) / len(lst))
