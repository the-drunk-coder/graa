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
from graa_base import *

class GraaParser():
    # type flags
    OVERLAY = "OL"
    NORMAL = "N"
    OL_APPLICATION = "OLA"
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
    node_def = node_id + Suppress("|") + node_type + Suppress("|") + Group(ZeroOrMore((func_param ^ var_assign) + Optional(param_divider)))
    node_def.setParseAction(lambda t: GraaParser.parse_node(t))
    transition_param = Word(nums)
    transition_param.setParseAction(lambda t: GraaParser.typify(t[0]))
    transition = Group(transition_param + Optional(param_divider + transition_param))
    ol_transition = Group((Word(nums) ^ func) + Optional(param_divider + (Word(nums) ^ func)))
    edge_def = node_id + Suppress("-") + transition + Suppress("->") + node_id
    edge_def.setParseAction(lambda t: GraaParser.parse_edge(t))
    ol_edge_def = node_id + Optional(Suppress("-") + ol_transition) + Suppress("->") + node_id
    ol_edge_def.setParseAction(lambda t: GraaParser.parse_ol_edge(t))
    ol_application = Group(OneOrMore(graph_id + Optional(param_divider))) + (Word("+") ^ Word("-")) + Group(OneOrMore(graph_id + Optional(param_divider)))
    ol_application.setParseAction(lambda t: GraaParser.parse_ol_application(t.asList()))
    line = node_def ^ edge_def ^ ol_node_def ^ ol_edge_def ^ ol_application
    line.setParseAction(lambda t: t.asList())
    # Additional rules to parse command inputs
    delay_command = Suppress("+") + Word(nums)
    delay_command.setParseAction(lambda t: GraaParser.typify(t[0]))
    start_command = graph_id ^ Group(graph_id + Suppress("|") + Word(alphas)) ^ Group(graph_id + Suppress("|") + delay_command) 
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
        return (GraaParser.NORMAL, graph_id, edge, source_node_id)
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
        return (GraaParser.NORMAL, graph_id, Node(node_id, node_params))
    def parse_ol_node(arg):        
        graph_id = arg[0]
        node_id = arg[1]
        node_params = {}
        for param in arg[2:]:
            node_params[param[0]] = param[1]
        # create and return node
        return (GraaParser.OVERLAY, graph_id, Node(node_id, node_params))
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
        return (GraaParser.OVERLAY, graph_id, edge, source_node_id)
    def parse_ol_application(arg):
        return (GraaParser.OL_APPLICATION, arg)
    def parse(arg):
        return GraaParser.line.parseString(arg)
    
"""
Dispatch parser output to session

"""
class GraaDispatcher():
    def __init__(self, session):
        self.session = session
        self.dispatcher_map = {}
        self.dispatcher_map[GraaParser.OVERLAY] = self.dispatch_overlay
        self.dispatcher_map[GraaParser.NORMAL] = self.dispatch_normal
        self.dispatcher_map[GraaParser.OL_APPLICATION] = self.dispatch_ol_application
        self.outfile = session.outfile
    def dispatch(self, parser_output):
        elem = parser_output[0]
        try:
            self.dispatcher_map[elem[0]](elem)
        except KeyError:
            print("Can't dispatch {}, no dispatcher present!".format(elem))        
    def dispatch_overlay(self, ol_elem):
        ol_id = ol_elem[1]
        if ol_id not in self.session.overlays:
            self.session.overlays[ol_id] = Graph()
            print("Initialized overlay with id: \'" + ol_id + "\'", file=self.outfile, flush=True)            
        # otherwise, dispatch the element
        overlay = self.session.overlays[ol_id]
        ol_content = ol_elem[2]
        if type(ol_content) is Edge:
            src = ol_elem[3]
            dst = ol_content.dest
            # initialize step counter with 0
            # content.meta = 0
            if src not in overlay.nodes or dst not in overlay.nodes:
                raise DispatcherError("Invalid overlay edge, source or destination node not present!")
            self.session.overlays[ol_id].add_edge(src, ol_content)
            print("Adding edge: {} to overlay: {}'".format(ol_content, ol_id), file=self.outfile, flush=True)
        elif type(ol_content) is Node:
            #initialize step counter with 0
            ol_content.meta = 0
            self.session.overlays[ol_id].add_node(ol_content)
            print("Adding node: {} to overlay: {}'".format(ol_content, ol_id), file=self.outfile, flush=True)
        for player_id in self.session.players:
            if ol_id in self.session.players[player_id].overlays:
                self.session.players[player_id].update_overlay(ol_id)                
    def dispatch_normal(self, elem):
        graph_id = elem[1]
        if graph_id not in self.session.graphs:
            self.session.graphs[graph_id] = Graph()
            print("Initialized graph with id: \'" + graph_id + "\'", file=self.outfile, flush=True)
        # otherwise, dispatch the element
        graph = self.session.graphs[graph_id]
        content = elem[2]        
        if type(content) is Edge:
            src = elem[3]
            dst = content.dest
            if src not in graph.nodes or dst not in graph.nodes:
                raise DispatcherError("Invalid edge, source or destination node not present!")
            print("Adding edge: {} to graph: {}'".format(content, graph_id), file=self.outfile, flush=True)
            self.session.graphs[graph_id].add_edge(src, content)                                                  
        elif type(content) is Node:
            print("Adding node: {} to graph: {}'".format(content, graph_id), file=self.outfile, flush=True)
            self.session.graphs[graph_id].add_node(content)                                                  
    def dispatch_ol_application(self, elem):
        graph_ids = elem[1][0]
        cmd = elem[1][1]
        overlay_ids = elem[1][2]
        for graph_id in graph_ids:            
            for overlay_id in overlay_ids:
                if cmd == "+":
                    try:
                        print("Adding overlay: {} to graph: {}'".format(overlay_id, graph_id), file=self.outfile, flush=True)
                        # if no player present for current graph, create one
                        if graph_id not in self.session.players:                            
                            self.session.players[graph_id] = GraaPlayer(self.session, graph_id, None)
                        self.session.players[graph_id].add_overlay(overlay_id)
                    except:
                        print("Couldn't add overlay!")
                        raise
                elif cmd == "-":
                    try:
                        print("Removing overlay: {} from graph: {}'".format(overlay_id, graph_id), file=self.outfile, flush=True)
                        self.session.players[graph_id].remove_overlay(overlay_id)
                    except:
                        print("Couldn't remove overlay!")
                        raise
                
# class for dispatcher errors                
class DispatcherError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return repr(self.message)
    
"""
if __name__ == "__main__":
    print(GraaParser.line.parseString("ol1|$1=func($1, b1, step, 0.1):vowel=func(2)"))
    print(GraaParser.line.parseString("d1|dirt:0:casio:1:vowel=o:d"))
    #node = GraaParser.node_def.parseString("d1|dirt:0:casio:1:vowel=o:d")
    #print(node[0][1].content)
    print(GraaParser.line.parseString("d1-100:100->d1"))
    #edge = edge_tup[1]
    #print(edge.dur)
    print(GraaParser.line.parseString("d1-100->d1"))
    print(GraaParser.line.parseString("d1->d1"))
    print(GraaParser.line.parseString("d1-100:func(b)->d1"))      
    print(GraaParser.line.parseString("d1-func():func(d)->d1"))
    #edge2 = edge_tup2[1]
    #print(edge2.dur)
    print(GraaParser.line.parseString("d+e"))
    print(GraaParser.line.parseString("d:a+e:w"))
"""    
