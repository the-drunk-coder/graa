from graa_structures import *
from graa_parser import *

if __name__ == "__main__":
    
    ol_node_line = "ol1|vowel=stepvow(step)"
    a = GraaParser.ol_node_def.parseString(ol_node_line)
    print(repr(a[0][2]))

    node_line = "d1|dirt~o:bd:0:vowel=a"
    b = GraaParser.node_def.parseString(node_line)
    print(repr(b[0][2]))
    
    edge_line_1 = "d1-100:100->d2"
    c = GraaParser.edge_def.parseString(edge_line_1)
    print(repr(c[0][2]))

    edge_line_2 = "d2-200->d3"
    d = GraaParser.edge_def.parseString(edge_line_2)
    print(repr(d[0][2]))
    
    edge_line_3 = "d1-xy(dur):zu(prob)->d2"
    e = GraaParser.ol_edge_def.parseString(edge_line_3)
    print(repr(e[0][2]))

    edge_line_4 = "d1->d2"
    f = GraaParser.ol_edge_def.parseString(edge_line_4)
    print(repr(f[0][2]))

    
    

    


    
    
