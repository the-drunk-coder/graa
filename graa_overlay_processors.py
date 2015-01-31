import copy, graa_overlay_functions

# replace named args, where kwargs is a dictionary of arguments
def replace_kwargs(kwargs, functions, step):
    # new empty dictionary, so orignal arguments won't be destroyed ... 
    new_kwargs = {}
    for arg_key in kwargs.keys():
        new_kwargs[arg_key] = process_mod_function(arg_key, kwargs[arg_key], step, functions)
    return new_kwargs
       
# replace anonymous args, where args is a list of arguments
def replace_args(args, functions, step):
    # generate identifiers for unnamed variables
    arg_vars = ["$" + str(i) for i in range(1, 1 + len(args))]
    # process variables
    processed_values = [process_mod_function(key, value, step, functions) for key, value in zip(arg_vars, args)]
    return processed_values

def process_mod_function(key, orig_value, step, functions):
    # print("PROCESS MOD: {} {} {} {}".format(key, orig_value, step, functions))
    # this is NOT a loop !!!
    if type(functions) is str:
        return orig_value
    if key in functions.keys():
        # get the function representation (list of strings)
        func_list = functions[key]
        # get the function from the modification module
        func = getattr(graa_overlay_functions,func_list[0])
        # replace step and variable id by actual value
        func_args = []
        for arg_id in func_list[1]:
            if arg_id == "step":
                func_args.append(step)
            elif arg_id == key:
                func_args.append(orig_value)
            else:
                func_args.append(arg_id)                                 
        return func(*func_args)
    else:
        return orig_value
