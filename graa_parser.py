from pyparsing import *
from graa_structures import *
from music21 import note, duration
# Hack to access variabled defined in the main routine. 
# Yes, i know this is not the way you ~should~ do this. Be quiet!
import __main__

class GraaParser():
    # command constants for dispatcher    
    EDGE = "edge"
    OVERLAY_NODE = "ol_node"
    NORMAL_NODE = "n_node"    
    # some literals
    PARAM_DIVIDER = Suppress(Literal(":"))
    LPAREN = Suppress(Literal("<"))
    RPAREN = Suppress(Literal(">"))
    # note shorthand
    pitch_class = Literal("c") ^ Literal("d") ^ Literal("e") ^ Literal("f") ^ Literal("g") ^ Literal("a") ^ Literal("b")
    pitch_mod = Literal("is") ^ Literal("es")  ^ Literal("isis") ^ Literal("eses")
    pitch = pitch_class + Optional(pitch_mod) + Word(nums).setParseAction(lambda t: GraaParser.typify(t[0]))
    pitch.setParseAction(lambda t: GraaParser.parse_pitch(t))
    dur_base = Literal("w") ^ Literal("h") ^ Literal("q") ^ Literal("e") ^ Literal("st") ^ Literal("ts") ^ Literal("sf") ^ (Suppress("ms") + Word(nums).setParseAction(lambda t: GraaParser.typify(t[0])))
    dur_mod = Literal("d") ^ Literal("dd")
    dur = Group(Optional(dur_mod) + dur_base)      
    # ids and variables
    gvar = Group(Suppress(Literal("?")) + Word(alphas))
    gvar.setParseAction(lambda t: GraaParser.parse_gvar(t.asList()))
    ivar = Group(Suppress(Literal("!")) + Word(alphas))
    ivar.setParseAction(lambda t: GraaParser.parse_ivar(t.asList()))
    lvar = Word("$." + alphanums)
    graph_id = Word(alphas)
    node_id = graph_id + Word(nums).setParseAction(lambda t: GraaParser.typify(t[0]))
    node_type = Word(alphanums)
    func_id = Word(alphanums)
    # function parsing
    func = Forward()
    param = gvar ^ ivar ^ pitch ^ lvar.setParseAction(lambda t: GraaParser.typify(t[0])) ^ func
    func_param = ZeroOrMore(param + Optional(PARAM_DIVIDER))
    func << func_id + LPAREN + func_param + RPAREN   
    func.setParseAction(lambda t: GraaParser.parse_func(t.asList()))    
    assign = lvar + Suppress("=") + param
    assign.setParseAction(lambda t: GraaParser.parse_assign(t.asList()))
    # node definitions
    ol_node_def = node_id + Suppress("|") + OneOrMore((assign + Optional(PARAM_DIVIDER)) ^ Literal("nil") ^ Literal("mute") ^ Literal("unmute"))
    ol_node_def.setParseAction(lambda t: GraaParser.parse_ol_node(t))
    node_def = node_id + Suppress("|") + node_type + Suppress("~") + Group(ZeroOrMore((gvar ^ ivar ^ pitch ^ lvar ^ assign) + Optional(PARAM_DIVIDER)))
    node_def.setParseAction(lambda t: GraaParser.parse_node(t))
    #edge definitions    
    transition = Group((Literal("nil") ^ param) + Optional(PARAM_DIVIDER + param))    
    edge_def = node_id + Optional(Suppress("-") + transition) + Suppress("->") + node_id
    edge_def.setParseAction(lambda t: GraaParser.parse_edge(t))    
    # line definition
    line = node_def ^ edge_def ^ ol_node_def  
    line.setParseAction(lambda t: t.asList())    
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
    def parse_gvar(arg):
        #print(arg[0])
        key = str(arg[0][0])        
        return Gvar(key)
    def parse_ivar(arg):        
        return getattr(__main__, arg[0][0])        
    def parse_func(arg):
        #print(arg)
        return Func(arg[0], arg[1:], {})
    def parse_assign(arg):
        return {arg[0] : arg[1]}
    def parse_pitch(arg):
        try:
            note_string = arg[0]
            if len(arg) == 3:
                note_string += acc_mapping[arg[1]]
            note_string += str(arg[-1])        
            parsed_note = GraaNote(note_string)
            return parsed_note
        except Exception as e:
            print(e)
    def parse_duration(arg):
        pass
        #tbd    
    def parse_node(arg):        
        graph_id = arg[0]
        node_id = arg[1]
        node_params = Func(arg[2], [], {})        
        for param in arg[3]:
            if isinstance(param, dict):
                node_params.kwargs.update(param)
            else:
                node_params.args.append(param)
        # create and return node
        return (GraaParser.NORMAL_NODE, graph_id, Node(graph_id, node_id, node_params))
    def parse_ol_node(arg):
        #print(arg)
        graph_id = arg[0]
        node_id = arg[1]
        node_params = {}
        for param in arg[2:]:
            if type(param) is str:
                node_params = param
            else:                
                node_params.update(param)
        node = Node(graph_id, node_id, node_params)
        return (GraaParser.OVERLAY_NODE, graph_id, node)
    def parse_edge(arg):
        #print(arg)
        graph_id = arg[0]
        source_node_id = arg[1]
        destination_node_id = arg[-1]
        edge = None
        if(len(arg) == 5):
            transition = arg[2]         
            edge = Edge(graph_id, source_node_id, destination_node_id, transition[0])
            if len(transition) == 2:
                edge.prob = transition[1]
        else:            
            edge = Edge(graph_id, source_node_id, destination_node_id, None)
        return (GraaParser.EDGE, graph_id, edge, source_node_id)    
    def parse(arg):
        return GraaParser.line.parseString(arg)


if __name__ == "__main__":
    #print(GraaParser.param.parseString("4"))
    #print(GraaParser.func.parseString("add<add<$3:4>:%as:4>"))
    #print(GraaParser.assign.parseString("$3=add<add<$3:4>:%as:>"))
    #print(GraaParser.assign.parseString("$step=5"))
    #print(GraaParser.node_def.parseString("d1|dirt~0:db:1:$gain=5"))
    #print(GraaParser.ol_node_def.parseString("d1|$3=add<$3:1>:$2=add<$2:1>"))
    #print("STRING: d1-add<$dur:add<1:%as>:4>:100->d1")
    #print(GraaParser.edge_def.parseString("d1-add<$dur:add<1:%as>:4>:100->d1"))
    #print(GraaParser.edge_def.parseString("d1->d1"))
    #print(GraaParser.line.parseString("d1-%t:100->d1"))
    #print(GraaParser.line.parseString("d1|rebuzz~150:100:245:$gain=10"))
    print(GraaParser.func.parseString("bounds<brownian<60:1>:500:300>"))
