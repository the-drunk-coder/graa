"""
d1|dirt:0:casio:1:vowel=a

=>

("d", Node(1, {type: "dirt", "args": [0, "casio", 1], "kwargs" : {"vowel" : "a"}}))

"""

"""
ol1|$1=func($1, step, 1):vowel=func2()

=>

("ol", Node(1, {"$1" : {function: "func", args:["$1", "step", 1]}
                "vowel" : {function: "func2", args:[]}}))

"""

"""
d1-100->d2

=> ("d", "d1", Edge("d2", 100, None))

d1-100:50->d2

=> ("d", "d1", Edge("d2", 100, 50))

d1-func(prob, 1):func(...)->d1


"""

from pyparsing import *
from graa_structures import *
from graa_dispatcher import GraaDispatcher

class GraaParser():
    # grammar rules (advanced ...)
    graph_id = Word(alphas)
    node_id = graph_id + Word(nums)
    node_type = Word(alphanums)
    func_id = Word(alphanums)
    param_divider = Suppress(":")
    func_param = Word("$." + alphanums)
    func_param.setParseAction(lambda t: GraaParser.typify(t[0]))
    func = Group(func_id + Group(Suppress("(") + ZeroOrMore(func_param + Optional(Suppress(","))) + Suppress(")")))
    func_assign = Group(func_param + Suppress("=") + func)
    func_assign.setParseAction(lambda t: t.asList())
    var_assign = Group(func_param + Suppress("=") + func_param)
    var_assign.setParseAction(lambda t: t.asList())
    ol_node_def = node_id + Suppress("|") + OneOrMore(func_assign + Optional(param_divider))
    ol_node_def.setParseAction(lambda t: GraaParser.parse_ol_node(t))
    node_def = node_id + Suppress("|") + node_type + Suppress("~") + Group(ZeroOrMore((func_param ^ var_assign) + Optional(param_divider)))
    node_def.setParseAction(lambda t: GraaParser.parse_node(t))
    transition_param = Word(nums)
    transition_param.setParseAction(lambda t: GraaParser.typify(t[0]))
    transition = Group(transition_param + Optional(param_divider + transition_param))
    ol_transition = Group((Word(nums) ^ func) + Optional(param_divider + (Word(nums) ^ func)))
    edge_def = node_id + Suppress("-") + transition + Suppress("->") + node_id
    edge_def.setParseAction(lambda t: GraaParser.parse_edge(t))
    ol_edge_def = node_id + Optional(Suppress("-") + ol_transition) + Suppress("->") + node_id
    ol_edge_def.setParseAction(lambda t: GraaParser.parse_ol_edge(t))
    ol_application = Group(OneOrMore(graph_id + Optional(param_divider))) + Suppress("+") + Group(OneOrMore(graph_id + Optional(param_divider)))
    ol_application.setParseAction(lambda t: GraaParser.parse_ol_application(t.asList()))
    ol_removal = Group(OneOrMore(graph_id + Optional(param_divider))) + Suppress("-") + Group(OneOrMore(graph_id + Optional(param_divider)))
    ol_removal.setParseAction(lambda t: GraaParser.parse_ol_removal(t.asList()))
    line = node_def ^ edge_def ^ ol_node_def ^ ol_edge_def ^ ol_application ^ ol_removal
    line.setParseAction(lambda t: t.asList())
    # Additional rules to parse command inputs
    delay_command = Suppress("@") + (Word(nums) ^ Word("now"))
    delay_command.setParseAction(lambda t: GraaParser.typify(t[0]))
    start_command = graph_id ^ Group(graph_id + delay_command) 
    #start_command.setParseAction(lambda t: t.asList())
    start_line = OneOrMore(start_command + Optional(param_divider))
    start_line.setParseAction(lambda t: t.asList())
    # convert string representation to actual (typed) value
    def typify(arg):
        #try int:
        try:
            return int(arg)
        except:
            pass
        # try float:
        try:
            return float(arg)
        except:
            pass
        # else, return arg as string
        return arg
    def parse_edge(arg):
        graph_id = arg[0]
        source_node_id = arg[1]
        destination_node_id = arg[-1]
        transition = arg[2]
        edge = Edge(destination_node_id, transition[0])
        if len(transition) == 2:
            edge.prob = transition[1]
        return (GraaDispatcher.NORMAL_EDGE, graph_id, edge, source_node_id)
    def parse_node(arg):        
        graph_id = arg[0]
        node_id = arg[1]
        node_params = {}
        node_params["type"] = arg[2]
        node_params["args"] = []
        node_params["kwargs"] = {}
        for param in arg[3]:
            if isinstance(param, list):
                node_params["kwargs"][param[0]] = param[1]
            else:
                node_params["args"].append(param)
        # create and return node
        return (GraaDispatcher.NORMAL_NODE, graph_id, Node(node_id, node_params))
    def parse_ol_node(arg):        
        graph_id = arg[0]
        node_id = arg[1]
        node_params = {}
        for param in arg[2:]:
            node_params[param[0]] = param[1]
        # create and return node
        return (GraaDispatcher.OVERLAY_NODE, graph_id, Node(node_id, node_params))
    def parse_ol_edge(arg):
        graph_id = arg[0]
        source_node_id = arg[1]
        destination_node_id = arg[-1]
        edge = None
        if(len(arg) == 5):
            transition = arg[2]
            edge = Edge(destination_node_id, transition[0])
            if len(transition) == 2:
                edge.prob = transition[1]
        else:
            edge = Edge(destination_node_id, 100)
        return (GraaDispatcher.OVERLAY_EDGE, graph_id, edge, source_node_id)
    def parse_ol_application(arg):
        return (GraaDispatcher.OL_APPLICATION, arg[0], arg[1])
    def parse_ol_removal(arg):
        return (GraaDispatcher.OL_REMOVAL, arg[0], arg[1])
    def parse(arg):
        return GraaParser.line.parseString(arg)
