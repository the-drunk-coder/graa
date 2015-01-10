# this is a comment

# graa is a line-based language

# BNF
<nonzero_digit> ::= 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9
<letter> ::= a | b | c | d | e | f | g | h | i | j | k | l | m | n | o | p | q | r | s | t | u | v | w | x | y | z
<digit> ::= 0 | <nonzero_digit>
<digits> ::= <digit> | <digit> <digits>
<pos_int> ::= <nonzero_digit> | <nonzero_digit> <digits>
<label> ::= <letter> | <letter> <label>
<node_id> ::= <label> <pos_int>
<node_desc> ::= <label> | <pos_int> | <node_desc> ":" <node_desc>   
<transition_params> ::= <pos_int> | <pos_int> ":" <pos_int>
<line> ::= <node_line> | <edge_line> | <cmd_line>
<node_line> ::= <node_id> ":" <node_desc> "\n"
<cmd_line> ::= <cmd> "(" <label> ")\n"
<edge_line> ::= <node_id> "-" <transition_params> "->" <node_id> "\n"

# format:
# node definition:
# node_id:node_type(:sample)(:type_definition)

# custom node type file

# node types:
# sam:  play a sample ... follow tidal conventions for effects and the like (append to node def) 
# buzz: sawtooth tone
# sin: sine tone 
# note: takes a note (pykopond) as input and maps it to an instrument

# edge definition:
# node_id-prob:abs_dur[, reld_dur]->node_id

# relative durations for syncing ?

# if probability is omitted, the probability will be split equally between possible options

# the graph is implicitly defined by defining the first node, that is, a node definition 'r2:sam:bd

# Example: define a graph with two sample nodes (special case: cyclic list).
r1:sam:bd:1
r2:sam:sn:1
r1-120:100->r2
r2-120:100->r1

play r:markov

# alternative with relative duration specification (follow pykopond conventions)
foo1:sam:bd:1
foo1-q:100->r1

# play modes
markov			# play in markov mode, using the transition probabilities.
man      	  	# play in manual mode, use 'nxt(r[, r1])' to pass next edge. if target is given,.
	    	  	# respective edge will be chosen. if not, the edge will be chosen by probability).
topo			# play nodes in topologically sorted order (ignoring cycles).
tsp			# calculate a tsp route and play nodes in that order. after all nodes have been visited, start anew.

# modifiers
invert			# invert direction of all non-self-referential edges in the graph.
sync			# play next node in graph on next beat
shift:<+|-><duration>	# shift graph forward or backward by specified absolute or relative duration
stretch:<factor>	# stretch durations by factor or list of factors (a generator function might be specified) 

# start modes (default: sync)
i | immidiate		# start graph as soon as possible
s | sync		# start on next beat

# time modes
a | absolute		# absoulte durations will be used
r | relative		# relative durations will be used

# commands
play <graph_id>:<play_mode>[:<start_mode>]		# play graph in specified mode. multiple pairs may be specified. 
stop <graph_id>						# stop and reset the graph (ditching eventual modifications). multiple graphs may be specified.
hold <graph_id>						# hold the graph in its current state. multiple graphs may be specified
next <graph_id>						# jump to next node in specified graph (ignore edge duration)
mod <graph_id>:<modifier>[:<mod_params>]		# apply a modifier to the graph. may be followed by mod params.
timemode <graph_id>:<mode> 				# set time mode (absolute, relative) for specified graph. for relative timing, durations will be quantized.
tempo <bpm>    						# set clock for relative timing (default: 119 bpm)
status							# print current status (graphs, playing graphs etc)
visualize						# visualize what's going on ...
rec <filename>						# record performance (not audio, but grap states)
load <filename>						# load performance from file
print <graph_id>					# print graph to pdf

# about duration specification and quantization
if a graph is specified with relative durations, but is played in absolute mode, the durations will be calculated in regard to the
current clock speed.
if a graph is specified with absoulte durations, but played in relative mode, the durations will be quantized to the nearest eight note, regarding the
current clock speed