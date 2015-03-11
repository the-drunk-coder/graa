from pyparsing import *
from graa_structures import *
from music21 import note, duration
# Hack to access variabled defined in the main routine. 
# Yes, i know this is not the way you ~should~ do this. Be quiet!
import __main__

class GraaParser():
    # command constants for dispatcher    
    EDGE = "edge"    
    NODE = "node"    
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
    # function parsing
    func = Forward()
    param = gvar ^ ivar ^ pitch ^ lvar.setParseAction(lambda t: GraaParser.typify(t[0])) ^ func
    func_param = ZeroOrMore(param + Optional(PARAM_DIVIDER))
    func << Word(alphanums) + LPAREN + func_param + RPAREN   
    func.setParseAction(lambda t: GraaParser.parse_func(t.asList()))    
    assign = lvar + Suppress("=") + param
    assign.setParseAction(lambda t: GraaParser.parse_assign(t.asList()))
    # node definitions
    sound_func = Word(alphas) + "~" + Group(ZeroOrMore((gvar ^ ivar ^ pitch ^ lvar ^ assign) + Optional(PARAM_DIVIDER)))
    mod_func = assign + Optional(PARAM_DIVIDER)
    ctrl_func = Word(alphas) + "#" + Group(ZeroOrMore((gvar ^ ivar ^ pitch ^ lvar ^ assign) + Optional(PARAM_DIVIDER)))
    slot = Suppress("|") + Group(sound_func ^ mod_func ^ ctrl_func)
    node_def = node_id + OneOrMore(slot)
    node_def.setParseAction(lambda t: GraaParser.parse_node(t))
    #edge definitions
    trans_dur = Group((param ^ Literal("nil")) + Optional(Suppress("|") + param))
    trans_prob = Group(Literal("%") + (param ^ Literal("nil")) + Optional(Suppress("|") + param))
    transition = Suppress("--") + Group(Optional(trans_dur) + Optional(trans_prob)) + Suppress("-->")
    edge_def = node_id + (transition ^ Suppress("-->")) + node_id
    edge_def.setParseAction(lambda t: GraaParser.parse_edge(t))    
    # line definition
    line = node_def ^ edge_def
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
        return Func("misc", arg[0], arg[1:], {})
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
        print("NODE: " + str(arg))
        graph_id = arg[0]
        node_id = arg[1]
        node_params = []
        for param in arg[2:]:            
            if isinstance(param[0], dict):
                node_params.append(param[0])
            else:
                kwargs = {}
                args = []
                for arg in param[2]:
                    if type(arg) is dict:                        
                        kwargs.update(arg)
                    else:
                        args.append(arg)
                node_params.append(Func(param[1], param[0], args, kwargs))
        # create and return node
        return (GraaParser.NODE, graph_id, Node(graph_id, node_id, node_params))    
    def parse_edge(arg):
        print("EDGE: " + str(arg))
        graph_id = arg[0]
        source_node_id = arg[1]
        destination_node_id = arg[-1]
        edge = Edge(graph_id, source_node_id, destination_node_id)
        if(len(arg) == 5):
            transition = arg[2]
            for elem in transition:
                if elem[0] == "%":
                    if elem[1] != "nil":
                        edge.prob = elem[1]
                    if len(elem) == 3:
                        edge.prob_mod = elem[2]
                else:
                    if elem[0] != "nil":
                        edge.dur = elem[0]
                    if len(elem) == 2:
                        edge.dur_mod = elem[1]            
        return (GraaParser.EDGE, graph_id, edge, source_node_id)    
    def parse(arg):
        return GraaParser.line.parseString(arg)


if __name__ == "__main__":
    #print(GraaParser.edge_def.parseString("guu1-->guu2"))
    #print(GraaParser.edge_def.parseString("guu1--500-->guu2"))
    #print(GraaParser.edge_def.parseString("guu1--%50-->guu2"))
    #print(GraaParser.edge_def.parseString("guu1--500%25-->guu2"))
    #print(GraaParser.edge_def.parseString("guu1--512|add<dur:25>-->guu2"))    
    #print(GraaParser.edge_def.parseString("guu1--512|add<dur:25>%25-->guu2"))
    #print(GraaParser.edge_def.parseString("guu1--%25|add<prob:10>-->guu2"))
    #print(GraaParser.edge_def.parseString("guu1--512|add<dur:25>%25|add<prob:10>-->guu2"))
    print(GraaParser.edge_def.parseString("guu1--nil|add<dur:25>%25|add<prob:10>-->guu2"))
    print(GraaParser.edge_def.parseString("guu1--512|add<dur:25>%nil|add<prob:10>-->guu2"))
    #print(GraaParser.node_def.parseString("guu1|disk~c4:500:50:gain=0.05:acc=0.5|play#guu:gaa|$3=add<$3:4>"))
