from pyparsing import *
from graa_structures import *
from music21 import note, duration

duration_mapping = { "q":1.0, "h":2.0,"w":4.0,"e":0.5, "st":0.25, "ts":0.125, "sf":0.0625 }
dot_mapping = { "d":1, "dd":2 }
inv_duration_mapping = { "quarter":"q", "half":"h","whole":"w","eight":"e", "16th":"st", "32th":"ts", "64th":"sf" }
inv_dot_mapping = {v: k for k, v in dot_mapping.items()}


# define note class to get representation right
class GraaNote(note.Note):    
    def __init__(self, *args, **kwargs):
        self.absolute_duration = None
        super().__init__(*args, **kwargs)
    def __repr__(self):
        note_string = self.nameWithOctave.lower()
        if self.absolute_duration != None:
            note_string += "ms" + str(self.absolute_duration)
        else:
            durtup = duration.dottedMatch(self.duration.quarterLength)
            if durtup[0] != False:
                note_string += inv_dot_mapping[durtup[0]]                        
            note_string += inv_duration_mapping[durtup[1]]            
        return note_string

class GraaParser():
    # command constants for dispatcher
    OVERLAY_EDGE = "ol_edge"
    NORMAL_EDGE = "n_edge"
    OVERLAY_NODE = "ol_node"
    NORMAL_NODE = "n_node"    
    # note shorthand
    pitch_class = Literal("c") ^ Literal("d") ^ Literal("e") ^ Literal("f") ^ Literal("g") ^ Literal("a") ^ Literal("b")
    pitch_mod = Literal("#") ^ Literal("-")  ^ Literal("##") ^ Literal("--")
    pitch = Group(pitch_class + Optional(pitch_mod) + Word(nums).setParseAction(lambda t: GraaParser.typify(t[0])))    
    dur_base = Literal("w") ^ Literal("h") ^ Literal("q") ^ Literal("e") ^ Literal("st") ^ Literal("ts") ^ Literal("sf") ^ (Suppress("ms") + Word(nums).setParseAction(lambda t: GraaParser.typify(t[0])))
    dur_mod = Literal("d") ^ Literal("dd")
    dur = Group(Optional(dur_mod) + dur_base)    
    note = pitch + dur
    note.setParseAction(lambda t: GraaParser.parse_note(t.asList()))
    # grammar rules (advanced ...)
    graph_id = Word(alphas)
    node_id = graph_id + Word(nums)
    node_type = Word(alphanums)
    func_id = Word(alphanums)
    param_divider = Suppress(":")
    func_param = Word("$." + alphanums) ^ note
    func_param.setParseAction(lambda t: GraaParser.typify(t[0]))
    func = Group(func_id + Group(Suppress("<") + ZeroOrMore(func_param + Optional(param_divider)) + Suppress(">")))
    func.setParseAction(lambda t: t.asList())
    func_assign = Group(func_param + Suppress("=") + func)
    func_assign.setParseAction(lambda t: t.asList())
    var_assign = Group(func_param + Suppress("=") + func_param)
    var_assign.setParseAction(lambda t: t.asList())
    ol_node_def = node_id + Suppress("|") + OneOrMore(func_assign + Optional(param_divider))
    ol_node_def.setParseAction(lambda t: GraaParser.parse_ol_node(t))
    node_def = node_id + Suppress("|") + node_type + Suppress("<") + Group(ZeroOrMore((func_param ^ var_assign) + Optional(param_divider))) + Suppress(">")
    node_def.setParseAction(lambda t: GraaParser.parse_node(t))
    transition_param = Word(nums)
    transition_param.setParseAction(lambda t: GraaParser.typify(t[0]))
    transition = Group(transition_param + Optional(param_divider + transition_param))
    ol_transition = Group((Word(nums) ^ func) + Optional(param_divider + (Word(nums) ^ func)))
    edge_def = node_id + Suppress("-") + transition + Suppress("->") + node_id
    edge_def.setParseAction(lambda t: GraaParser.parse_edge(t))
    ol_edge_def = node_id + Optional(Suppress("-") + ol_transition) + Suppress("->") + node_id
    ol_edge_def.setParseAction(lambda t: GraaParser.parse_ol_edge(t))    
    line = node_def ^ edge_def ^ ol_node_def ^ ol_edge_def  
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
    def parse_note(arg):
        try:
            note_string = arg[0][0]
            if len(arg[0]) == 3:
                note_string += arg[0][1]
            note_string += str(arg[0][-1])        
            parsed_note = GraaNote(note_string)
            parsed_duration = arg[1]
            if len(arg[1]) == 1 and type(arg[1][0]) is int:
                parsed_note.absolute_duration = arg[1][0]
            elif len(arg[1]) == 1 and type(arg[1][0]) is str:
                parsed_note.duration = duration.Duration(duration_mapping[arg[1][0]])
            elif len(arg[1]) == 2:
                parsed_note.duration = duration.Duration(duration_mapping[arg[1][1]])
                parsed_note.duration.dots = dot_mapping[arg[1][0]]        
            return parsed_note
        except Exception as e:
            print(e)
    def parse_edge(arg):
        # 0 = graph_id, 1 = source, -1 = dest, 2 = transition
        edge = Edge(arg[0], arg[1], arg[-1], arg[2][0])
        if len(arg[2]) == 2:
            edge.prob = arg[2][1]        
        return (GraaParser.NORMAL_EDGE, arg[0], edge, arg[1])
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
        return (GraaParser.NORMAL_NODE, graph_id, Node(graph_id, node_id, node_params))
    def parse_ol_node(arg):        
        graph_id = arg[0]
        node_id = arg[1]
        node_params = {}
        for param in arg[2:]:
            node_params[param[0]] = param[1]        
        return (GraaParser.OVERLAY_NODE, graph_id, Node(graph_id, node_id, node_params))
    def parse_ol_edge(arg):
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
        return (GraaParser.OVERLAY_EDGE, graph_id, edge, source_node_id)    
    def parse(arg):
        return GraaParser.line.parseString(arg)


if __name__ == "__main__":
    print(GraaParser.note.parseString("c#4q"))
    print(GraaParser.note.parseString("c-4ddq"))
    print(GraaParser.note.parseString("c4ms400"))
