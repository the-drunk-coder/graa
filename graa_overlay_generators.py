

"""
Generators for specific overlays.
"""

def brownian(var, inc_step, min_bound, max_bound):
    """
    A simpliefied version of a brownian motion, with incrementing steps for scaling.

    Also, you can define bounds.

    If the value hits a bound, it will be returned without modification.

    Works only if you use it with permanent overlay.
    
    """
    
    
    
