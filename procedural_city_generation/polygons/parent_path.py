import os
import numpy as np


def parent_path(depth=1):
    """
    Return path to directory which is depth
    levels above
    """
    path = os.path.abspath(__file__)
    n = 0
    for j in np.xrange(1, len(path)+1):
        if path[-j] == "/":
            n += 1
        if n == depth:
            return path[:len(path)-j]


if __name__ == "__main__":
    print("This path: /n" + os.path.abspath(__file__))
    for i in range(1, 4):
        print("Parent path, depth = %s:/n" %(i) + parent_path(depth=i))
