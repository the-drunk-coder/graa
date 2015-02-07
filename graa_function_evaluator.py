"""

This could probably be done more directly with eval(..),
but i think it's clearer this way ...

"""

from graa_structures import *
from graa_sound_functions import *
from graa_overlay_functions import *
from graa_session import GraaSession as session
# Hack to access variabled defined in the main routine. 
# Yes, i know this is not the way you ~should~ do this. Be quiet!
import __main__


def process_arguments(func, arg_funcs, step):
    #print("PROC " + str(func))
    for i in range(0, len(func.args)):
        key = "$" + str(i+1) 
        if key in arg_funcs:
            #print("eval: " + str(key))
            orig_value = func.args[i]
            #print("ORIG_VAL " + str(orig_value))
            func.args[i] = func_eval(type(orig_value), arg_funcs[key], {key:orig_value, "$step":step, "$time":session.now})
            #print("MODIFIED VAL: " + str(func.args[i]))
    for key in func.kwargs:        
        if key in arg_funcs:
            orig_value = func.kwargs[key]
            func.kwargs[key] = func_eval(type(orig_value), arg_funcs[key], {key:orig_value, "$step":step, "$time":session.now})
    return func
            
def arg_eval(orig_type, arg, local_vars):
    if type(arg) is Func:
        return func_eval(orig_type, arg, local_vars)
    elif type(arg) is Gvar:
        # Again, i know this is not the way you ~should~ do this. Shut up!
        return(getattr(__main__, arg.key))
    else:
        return arg


"""
Maybe i should overthink this, as i don't really like copying the args for replacement, seems like an unnecessary
step ... but for now, it works ... 
"""
# eval a function with a dict of local vars, maintaining an expected type ...
def func_eval(orig_type, func, local_vars):
    #print(orig_type)
    #print("EVAL " + str(func))
    #print(local_vars)
    #print(func.args)
    # recursively evaluate argument functions
    trans_args = copy.deepcopy(func.args)
    trans_kwargs = copy.deepcopy(func.kwargs)
    for i in range(0, len(func.args)):        
        # replace local variables from dict
        if func.args[i] in local_vars.keys():
            #print("REPLACING!!")
            trans_args[i] = local_vars[func.args[i]]        
        else:
            trans_args[i] = arg_eval(type(func.args[i]), func.args[i], local_vars)
    for key in func.kwargs:        
        # replace local variables from dict
        if func.kwargs[key] in local_vars.keys():            
            trans_kwargs[key] = local_vars[func.kwargs[key]]
        else:
            trans_kwargs[key] = arg_eval(type(func.kwargs[key]), func.kwargs[key], local_vars)   
    if orig_type != None:
        ret = orig_type(eval(func.name)(*trans_args, **trans_kwargs))
        #print("RET " + str(ret))
        return ret    
    else:
        ret = eval(func.name)(*trans_args, **trans_kwargs)
        #print("VOIDRET " + str(ret))
        return ret

    
"""
def add(a, b):
    return a + b

if __name__ == "__main__":
    local_vars = {"$step": 1, "$time" : 10000100}
    a = 30

    func = Func("add", [Func("add", ["%a", "$time"]), "$step"])
    print(func_eval(func, local_vars))

"""
   
