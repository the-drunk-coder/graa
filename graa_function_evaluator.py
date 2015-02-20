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
#from graa_parser import *

def process_arguments(func, arg_funcs, step):
    #print("PROC " + str(func))
    for i in range(0, len(func.args)):
        key = "$" + str(i+1) 
        if key in arg_funcs:
            #print("eval: " + str(key))
            orig_value = func.args[i]
            #print("ORIG_VAL " + str(orig_value))
            func.args[i] = func_eval(type(orig_value), arg_funcs[key], {key:orig_value, "step":step, "time":session.now})
            #print("MODIFIED VAL: " + str(func.args[i]))
    for key in func.kwargs:        
        if key in arg_funcs:
            orig_value = func.kwargs[key]
            func.kwargs[key] = func_eval(type(orig_value), arg_funcs[key], {key:orig_value, "step":step, "time":session.now})
    return func
            
def arg_eval(orig_type, arg, local_vars):
    #print("EVALUATING ARGUMENT: " + str(arg))
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
    for i in range(0, len(trans_args)):        
        # replace local variables from dict
        if  trans_args[i] in local_vars.keys():
            #print("REPLACING!!")
            trans_args[i] = local_vars[trans_args[i]]
            #print("REPLACED: " + str(trans_args))
        else:
            #print("EVALUATING!!")
            trans_args[i] = arg_eval(type(trans_args[i]), trans_args[i], local_vars)
            #print("EVALUATED" + str(trans_args))
    for key in trans_kwargs:        
        #replace local variables from dict
        if trans_kwargs[key] in local_vars.keys():            
            trans_kwargs[key] = local_vars[trans_kwargs[key]]
        else:
            trans_kwargs[key] = arg_eval(type(trans_kwargs[key]), trans_kwargs[key], local_vars)   
    if orig_type != None and orig_type != Func and orig_type != GraaNote:
        #print("NAME:" + str(func.name) + " " + str(orig_type))
        ret = orig_type(eval(func.name)(*trans_args, **trans_kwargs))
        #print("RET " + str(ret))
        return ret    
    else:
        ret = eval(func.name)(*trans_args, **trans_kwargs)
        #print("VOIDRET " + str(ret))
        return ret

    

"""def add(a, b):
    return a + b
"""
if __name__ == "__main__":
    func = GraaParser.func.parseString("wrap<brownian<c4:10>:60:50>")
    #func = GraaParser.func.parseString("brownian<c4:2>")
    #func = GraaParser.func.parseString("bounds<10:500:300>")
    #func = GraaParser.func.parseString("brownian<10:5>")    
    print(func_eval(GraaNote, func[0], {}))   
